# Phase 1: Project Setup — Kids Video Enhancer Tool

## Overview
This phase sets up a clean, modular project structure with:
- **Backend:** FastAPI with a health check route
- **Frontend:** React + Vite with simple UI
- **CORS enabled** for frontend-backend communication

## Folder Structure

```
animated-videos/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py        # Health check endpoint
│   │   ├── services/
│   │   │   └── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html               # HTML entry point
│   ├── index.tsx                # React entry point
│   ├── index.css                # Global styles
│   ├── App.tsx                  # Main app component
│   ├── App.css                  # App styles
│   ├── vite.config.ts           # Vite config with API proxy
│   ├── tsconfig.json            # TypeScript config
│   ├── tsconfig.node.json       # TypeScript config for build tools
│   └── package.json             # Dependencies
│
└── README.md
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - The API will be available at `http://localhost:8000`
   - Swagger UI docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   - The app will be available at `http://localhost:3000`

## How to Test

### Test Backend

**Option 1: cURL (Health Check)**
```bash
curl http://localhost:8000/health
```
Expected output:
```json
{"status": "OK"}
```

**Option 2: Swagger UI**
- Open `http://localhost:8000/docs` in your browser
- Click on the `/health` endpoint and hit "Try it out"

**Option 3: Test Root Endpoint**
```bash
curl http://localhost:8000/
```
Expected output:
```json
{"message": "Kids Video Enhancer API is running"}
```

### Test Frontend

1. Open `http://localhost:3000` in your browser
2. You should see:
   - **Title:** "Kids Video Enhancer Tool"
   - **Status:** "App is running"
   - **API Status:** Should change from "checking..." to "Backend is connected!" (if backend is running)
   - **Features list:** Shows upcoming features

### End-to-End Test

1. Start backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In another terminal, start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open browser to `http://localhost:3000`
4. Verify:
   - Page loads without errors
   - "API Status" shows "Backend is connected!"
   - Both servers are running without issues

## Expected Output

### Backend Console
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete
```

### Frontend Console
```
  VITE v5.0.8  ready in 456 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h + enter to show help
```

### Browser (Frontend)
```
Kids Video Enhancer Tool

App is running
API Status: Backend is connected!

Features (Coming Soon)
• Upload normal videos
• Apply cartoon-style filters
• Add auto-generated subtitles
• Overlay stickers and emojis
• Add sound effects
• Download enhanced video
```

## What's Done
✅ Backend FastAPI structure with health check
✅ Frontend React + Vite with UI
✅ CORS configuration for cross-origin requests
✅ API proxy in Vite (frontend can call backend at `/api/*`)
✅ No video processing logic yet

## Next Phase
Phase 2 will add the video processing pipeline:
- Upload API endpoint
- Frame extraction using OpenCV
- Video reconstruction

---

**Notes:**
- Backend runs on port **8000**
- Frontend runs on port **3000**
- No video dependencies installed yet (will add in Phase 2)
- Code is production-ready and modular
