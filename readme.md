# Kids Video Enhancer Tool

Convert normal videos into animated, kid-friendly content with cartoon filters, subtitles, stickers, and sound effects.

## 🎯 Features (Planned)
- Upload normal videos
- Apply cartoon-style filters
- Auto-generate subtitles
- Add emoji/sticker overlays
- Enhance with sound effects
- Download processed videos

## 🏗️ Architecture

**Backend:** FastAPI + Python
- Video upload API
- Frame extraction (OpenCV)
- Video reconstruction (FFmpeg)
- Cartoon filters (OpenCV → CartoonGAN)
- Subtitle generation (Whisper)
- Effects overlay (FFmpeg)

**Frontend:** React + Vite + Next.js
- Video upload UI
- Processing status
- Preview + download

**Storage:** Local (MVP) → AWS S3 (later)

## 📋 Project Phases

### ✅ Phase 1: Project Setup
- FastAPI backend with health check
- React + Vite frontend
- CORS configuration

**Documentation:** [PHASE_1_SETUP.md](./PHASE_1_SETUP.md)

### ✅ Phase 2: Video Upload + Processing
- POST /upload endpoint
- Frame extraction (OpenCV)
- Video reconstruction (FFmpeg)
- No filters yet

**Documentation:** [PHASE_2_UPLOAD.md](./PHASE_2_UPLOAD.md)

### 🔄 Phase 3: Cartoon Stylization (Next)
- OpenCV cartoon filter
- CartoonGAN upgrade path
- Apply effects to frames

### ⏳ Future Phases
- Phase 4: Subtitle generation
- Phase 5: Sticker/emoji overlays
- Phase 6: Sound effects
- Phase 7: Frontend UI
- Phase 8: Job queue (async processing)
- Phase 9: Storage + export
- Phase 10: Deployment

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

## 📝 System Requirements

- Python 3.8+
- Node.js 16+
- **FFmpeg** (required for video processing)
  - macOS: `brew install ffmpeg`
  - Windows: `choco install ffmpeg` or download from ffmpeg.org
  - Linux: `sudo apt-get install ffmpeg`

## 🧪 Testing

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Upload test video
curl -X POST http://localhost:8000/upload -F "file=@video.mp4"
```

### Test Frontend
- Open http://localhost:3000
- Should show app status and API connection

## 📂 File Storage

- **Input videos:** `uploads/`
- **Output videos:** `uploads/output/`
- **Temporary frames:** Auto-cleanup in system temp dir

## 🔧 Tech Stack
- Backend: FastAPI, uvicorn, python-multipart
- Video: OpenCV, FFmpeg
- Frontend: React, Vite, TypeScript
- AI/ML (Phase 3+): PyTorch, CartoonGAN, Whisper

## 📄 License
MIT