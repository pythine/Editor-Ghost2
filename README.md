# Template Video Editor

Web editor untuk membuat video dari foto/video dengan pola template:
- Frontend: Next.js + React + Tailwind CSS
- Backend: FastAPI
- Processing: FFmpeg
- Video analysis: OpenCV
- Beat detection: librosa
- Optional template acquisition: yt-dlp

## Penting
Video dari YouTube/TikTok tidak selalu mengandung informasi project/efek aslinya. Engine ini menganalisis video sumber dan merekonstruksi timing berdasarkan durasi, frame changes dan beat audio. Untuk konten pihak ketiga, gunakan hanya media yang memang boleh Anda unduh/olah.

## 1. Prasyarat Windows

Install:
1. Node.js LTS: https://nodejs.org/
2. Python 3.11 atau 3.12 direkomendasikan untuk backend.
3. FFmpeg dan pastikan `ffmpeg` serta `ffprobe` tersedia di PATH.

Cek:
```powershell
node --version
npm --version
python --version
ffmpeg -version
ffprobe -version
```

## 2. Backend

Buka terminal VS Code:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Jika PowerShell menolak aktivasi:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

Backend:
http://127.0.0.1:8000

Docs:
http://127.0.0.1:8000/docs

## 3. Frontend

Terminal baru:
```powershell
cd frontend
npm install
npm run dev
```

Buka:
http://localhost:3000

## 4. Cara memakai

1. Masukkan link template YouTube/TikTok atau upload file template.
2. Klik Analisis Template.
3. Masukkan beberapa foto/video.
4. Pilih mode template.
5. Klik Buat Video.
6. Tunggu rendering.
7. Preview dan Download.

## 5. FFmpeg

FFmpeg harus berada di PATH. Jika belum, install FFmpeg lalu restart VS Code.

## Arsitektur

frontend/
  Next.js UI

backend/
  main.py
  template_engine.py
  video_processor.py
  beat_detector.py
  media_utils.py

outputs/
  hasil MP4
