# Design Direction: Tubi (YouTube Downloader)

## Overview & Soul
Tubi adalah utilitas web pengunduh media video dan audio YouTube yang mengutamakan kecepatan, kejelasan hierarki, dan fungsionalitas tanpa distraksi.

## Design Read
Reading this as: Web utility video & audio downloader for everyday users, in a minimal functional editorial style, dial ENERGY 1 / RHYTHM 2 / MOTION 1.

## Dials
- **ENERGY**: 1 (Tenang, fungsional, berorientasi alat utilitas)
- **RHYTHM**: 2 (Struktur konsisten: hero input terpusat, kartu info video responsif, panel opsi format)
- **MOTION**: 1 (Transisi status halus dan hover state fungsional, tanpa animasi loop yang berlebihan)

## Palette
- **Background**: `#0b0d13` (Deep neutral slate)
- **Surface / Card**: `#131620` (Matte elevated slate)
- **Surface Border**: `#212638` (Subtle boundary line)
- **Foreground Text**: `#f3f4f6` (High contrast primary text, WCAG AA compliant)
- **Muted Text**: `#94a3b8` (Secondary information text)
- **Accent**: `#e11d48` (Crimson rose, aksen tunggal untuk tombol aksi unduh dan tab aktif)
- **Success / Badge**: `#10b981` (Status indikator netral)
- **Error**: `#ef4444` (Notifikasi validasi URL atau kegagalan fetch)

## Typography
- System / Inter sans-serif stack (`font-sans`), bobot 400 (regular), 500 (medium), dan 600 (semibold).
- Tidak menggunakan font monospace berlebihan atau huruf kapital dengan tracking ekstrim.

## Identity Motif
- Layout satu kolom fokus utilitas (Single focused workflow).
- Tag resolusi dan format berbentuk label monokrom bersih dengan indikator ukuran berkas.
- Tabs pemisah yang tegas antara video (MP4) dan audio (MP3).
