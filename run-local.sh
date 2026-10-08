#!/bin/bash
# Script utilitas untuk menjalankan Tubi (Backend + Frontend) di lokal secara bersamaan

echo "=== Menjalankan Tubi (Lokal) ==="

# Bersihkan proses latar belakang saat script dihentikan (Ctrl+C)
cleanup() {
    echo ""
    echo "Menghentikan layanan..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# 1. Jalankan Backend
echo "[1/2] Menjalankan Backend FastAPI di http://127.0.0.1:8000 ..."
(cd backend && python3 -m uvicorn main:app --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

sleep 2

# 2. Jalankan Frontend
echo "[2/2] Menjalankan Frontend SvelteKit di http://localhost:5173 ..."
(cd frontend && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONTEND_PID=$!

echo ""
echo "Aplikasi siap diakses di: http://localhost:5173"
echo "Tekan Ctrl+C untuk menghentikan server."

wait
