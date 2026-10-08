import asyncio
import os
import re
import shutil
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
import yt_dlp

app = FastAPI(
    title="Tubi API",
    description="Backend service for YouTube video and audio extraction and streaming",
    version="1.0.0"
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env.strip() == "*":
    origins = ["*"]
else:
    origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR_ROOT = "/tmp/tubi_downloads"
os.makedirs(TEMP_DIR_ROOT, exist_ok=True)

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com/(watch\?.*v=|shorts/|embed/|v/)|youtu\.be/)[a-zA-Z0-9_-]{11}"
)


class InfoRequest(BaseModel):
    url: str


def format_duration(seconds: Optional[int]) -> str:
    if not seconds or seconds < 0:
        return "Live / Unknown"
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else "tubi_media"


def cleanup_directory(path: str):
    if os.path.exists(path):
        try:
            shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass


def extract_info_sync(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "noplaylist": True,
        "socket_timeout": 15,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Tubi Media Downloader Backend",
        "version": "1.0.0"
    }


@app.post("/api/info")
async def get_video_info(payload: InfoRequest):
    url = payload.url.strip()
    if not YOUTUBE_REGEX.match(url):
        raise HTTPException(
            status_code=400,
            detail="URL yang dimasukkan bukan tautan YouTube yang valid."
        )

    try:
        info = await asyncio.to_thread(extract_info_sync, url)
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Private video" in error_msg:
            detail = "Video ini berstatus privat dan tidak dapat diakses."
        elif "Sign in to confirm your age" in error_msg:
            detail = "Video ini memiliki pembatasan usia (age-restricted)."
        elif "Video unavailable" in error_msg:
            detail = "Video tidak tersedia atau telah dihapus oleh pemiliknya."
        else:
            detail = f"Gagal mengekstrak informasi video: {error_msg.split(';')[-1].strip()}"
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")

    duration_sec = info.get("duration")
    duration_str = format_duration(duration_sec)

    best_thumb = info.get("thumbnail")
    thumbnails = info.get("thumbnails", [])
    if thumbnails:
        valid_thumbs = [t for t in thumbnails if t.get("url")]
        if valid_thumbs:
            best_thumb = valid_thumbs[-1]["url"]

    available_formats = info.get("formats", [])
    max_height = 0
    available_heights = set()
    for f in available_formats:
        h = f.get("height")
        if h and isinstance(h, int):
            available_heights.add(h)
            if h > max_height:
                max_height = h

    target_resolutions = [
        {"quality": "1080p", "height": 1080, "label": "Full HD"},
        {"quality": "720p", "height": 720, "label": "HD"},
        {"quality": "480p", "height": 480, "label": "SD"},
        {"quality": "360p", "height": 360, "label": "SD Low"},
    ]

    video_options = []
    for res in target_resolutions:
        if max_height >= res["height"] or not available_heights or res["height"] == 720:
            video_options.append({
                "quality": res["quality"],
                "height": res["height"],
                "label": res["label"],
                "ext": "mp4",
                "type": "video"
            })

    if not video_options:
        video_options.append({
            "quality": "best",
            "height": max_height or 720,
            "label": "Kualitas Terbaik",
            "ext": "mp4",
            "type": "video"
        })

    audio_options = [
        {"quality": "320k", "bitrate": "320 kbps", "label": "Kualitas Maksimal", "ext": "mp3", "type": "audio"},
        {"quality": "192k", "bitrate": "192 kbps", "label": "Kualitas Standar", "ext": "mp3", "type": "audio"},
        {"quality": "128k", "bitrate": "128 kbps", "label": "Hemat Kuota", "ext": "mp3", "type": "audio"},
    ]

    return {
        "id": info.get("id"),
        "title": info.get("title") or "Video YouTube",
        "uploader": info.get("uploader") or info.get("channel") or "Unknown Creator",
        "duration": duration_sec,
        "duration_formatted": duration_str,
        "thumbnail": best_thumb,
        "view_count": info.get("view_count"),
        "url": info.get("webpage_url") or url,
        "video_formats": video_options,
        "audio_formats": audio_options,
    }


def download_media_sync(url: str, media_type: str, quality: str, out_dir: str) -> str:
    template = os.path.join(out_dir, "%(title).100s.%(ext)s")
    has_ffmpeg = bool(shutil.which("ffmpeg"))

    if media_type == "audio":
        bitrate = quality if quality in ["320k", "192k", "128k"] else "192k"
        num_bitrate = bitrate.replace("k", "")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": template,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        if has_ffmpeg:
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": num_bitrate,
                }
            ]
    else:
        height_map = {"1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
        target_h = height_map.get(quality, 720)
        if has_ffmpeg:
            format_str = f"bestvideo[height<={target_h}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={target_h}]+bestaudio/best[height<={target_h}]/best"
            ydl_opts = {
                "format": format_str,
                "outtmpl": template,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "postprocessor_args": ["-c:a", "aac"],
            }
        else:
            format_str = f"best[height<={target_h}]/best/bestvideo[height<={target_h}]/bestvideo"
            ydl_opts = {
                "format": format_str,
                "outtmpl": template,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    files = [f for f in os.listdir(out_dir) if not f.endswith(".part") and not f.endswith(".ytdl")]
    if not files:
        raise RuntimeError("File hasil unduhan tidak ditemukan di direktori sementara.")

    files.sort(key=lambda x: os.path.getmtime(os.path.join(out_dir, x)), reverse=True)
    return os.path.join(out_dir, files[0])


@app.get("/api/download")
async def download_media(
    url: str = Query(..., description="Tautan video YouTube"),
    type: str = Query("video", pattern="^(video|audio)$", description="Format tujuan: video atau audio"),
    quality: str = Query("720p", description="Pilihan kualitas (1080p, 720p, 480p, 360p untuk video, 320k, 192k, 128k untuk audio)"),
    title: Optional[str] = Query(None, description="Nama file khusus jika disediakan"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    if not YOUTUBE_REGEX.match(url):
        raise HTTPException(
            status_code=400,
            detail="URL YouTube tidak valid."
        )

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR_ROOT, job_id)
    os.makedirs(job_dir, exist_ok=True)

    try:
        downloaded_file = await asyncio.to_thread(
            download_media_sync, url, type, quality, job_dir
        )
    except Exception as e:
        cleanup_directory(job_dir)
        raise HTTPException(
            status_code=500,
            detail=f"Proses download gagal diproses: {str(e)}"
        )

    if not os.path.exists(downloaded_file):
        cleanup_directory(job_dir)
        raise HTTPException(status_code=500, detail="File yang diunduh tidak ditemukan.")

    ext = os.path.splitext(downloaded_file)[1].lstrip(".") or ("mp3" if type == "audio" else "mp4")
    media_type = "audio/mpeg" if ext == "mp3" else "video/mp4"

    raw_filename = title if title else os.path.splitext(os.path.basename(downloaded_file))[0]
    safe_name = sanitize_filename(raw_filename)
    final_filename = f"{safe_name}.{ext}"

    # Clean up the temporary folder after client completes download
    background_tasks.add_task(cleanup_directory, job_dir)

    return FileResponse(
        path=downloaded_file,
        media_type=media_type,
        filename=final_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{final_filename}"',
            "Cache-Control": "no-cache",
        }
    )
