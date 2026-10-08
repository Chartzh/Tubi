# Tubi: Fullstack YouTube Video & Audio Downloader

Tubi adalah aplikasi web pengunduh video dan audio YouTube yang siap di-deploy ke cloud, dirancang dengan arsitektur modern yang memisahkan Frontend dan Backend secara decoupled.

- **Frontend**: SvelteKit + Tailwind CSS (Adapter: `@sveltejs/adapter-vercel`)
- **Backend**: FastAPI + `yt-dlp` + `ffmpeg` (Dockerized)

---

## Struktur Direktori

```text
Tubi/
├── DESIGN.md               # Spesifikasi visual & panduan antislop
├── README.md               # Dokumentasi dan panduan deployment
├── .gitignore              # Git ignore rules
│
├── backend/
│   ├── main.py             # FastAPI server dengan endpoint /api/info dan /api/download
│   ├── requirements.txt    # Dependensi Python
│   ├── Dockerfile          # Image berbasis python:3.11-slim + ffmpeg
│   ├── render.yaml         # Blueprint deployment untuk Render.com
│   ├── .dockerignore       # Docker ignore rules
│   └── .env.example        # Template variabel lingkungan backend
│
└── frontend/
    ├── src/
    │   ├── app.html        # Shell HTML dengan font Inter
    │   ├── app.css         # Styling global Tailwind
    │   └── routes/
    │       ├── +layout.svelte
    │       └── +page.svelte# Antarmuka Tubi (Input, Card Info, Tabs MP4/MP3)
    ├── svelte.config.js    # Konfigurasi @sveltejs/adapter-vercel
    ├── vite.config.js      # Konfigurasi Vite dev/build
    ├── tailwind.config.js  # Konfigurasi palet warna Tubi
    ├── postcss.config.js   # Konfigurasi PostCSS
    ├── package.json        # Dependensi dan scripts frontend
    └── .env.example        # Konfigurasi PUBLIC_API_URL
```

---

## 🚀 Panduan Deployment ke Cloud

### 1. Deploy Backend (Render / Koyeb)

Pilih salah satu layanan hosting backend berbasis Docker berikut:

#### Opsi A: Render (Menggunakan `render.yaml` atau Web Service Docker)
1. Push project Tubi ini ke repositori Git Anda (GitHub / GitLab).
2. Buka dashboard [Render](https://dashboard.render.com).
3. Klik **New +** > **Web Service**.
4. Hubungkan repositori Git Anda.
5. Konfigurasi service:
   - **Environment**: Docker
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`
   - **Plan**: Free
6. Pada bagian **Environment Variables**, tambahkan:
   - `ALLOWED_ORIGINS`: `*` (atau isi domain Vercel frontend Anda, contoh: `https://tubi-app.vercel.app`)
7. Klik **Create Web Service**. Tunggu proses build selesai dan salin URL service (contoh: `https://tubi-backend.onrender.com`).

#### Opsi B: Koyeb
1. Buka [Koyeb Console](https://app.koyeb.com).
2. Buat App baru dengan sumber **GitHub**.
3. Pilih repositori Anda, arahkan **Work directory** ke `backend`.
4. Pilih metode build **Dockerfile**.
5. Tambahkan environment variable `PORT` = `8000` dan `ALLOWED_ORIGINS` = `*`.
6. Klik **Deploy** dan catat URL publik yang dihasilkan.

---

### 2. Deploy Frontend (Vercel)

Frontend telah dikonfigurasi menggunakan adapter resmi `@sveltejs/adapter-vercel`.

1. Buka dashboard [Vercel](https://vercel.com) dan klik **Add New** > **Project**.
2. Hubungkan repositori Git project ini.
3. Pada halaman konfigurasi project:
   - **Root Directory**: Klik **Edit** dan pilih folder `frontend`.
   - **Framework Preset**: Vercel akan otomatis mengenali SvelteKit.
4. Pada bagian **Environment Variables**, tambahkan variabel berikut:
   - Key: `PUBLIC_API_URL`
   - Value: URL Backend dari langkah 1 (contoh: `https://tubi-backend.onrender.com` tanpa tanda garis miring di akhir).
5. Klik tombol **Deploy**.
6. Web app Tubi langsung aktif dan siap digunakan secara publik.

---

## 💻 Menjalankan di Komputer Lokal (Local Development)

### Prasyarat
- Node.js 18+ & npm
- Python 3.11+
- `ffmpeg` (terpasang di PATH sistem operasi Anda untuk konversi audio/video lokal)

### Menjalankan Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Backend akan aktif di `http://127.0.0.1:8000`. Cek endpoint status di `http://127.0.0.1:8000/`.

### Menjalankan Frontend
```bash
cd frontend
npm install
npm run dev
```
Buka browser di `http://localhost:5173`. Frontend akan langsung terhubung ke backend lokal `http://localhost:8000`.

---

## 🔒 Kebijakan & Lisensi
Project ini dibuat untuk tujuan pembelajaran dan utilitas pribadi. Harap patuhi hak cipta dan ketentuan layanan dari YouTube dan kreator konten.
