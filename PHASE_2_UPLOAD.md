# Phase 2: Video Upload + Processing Pipeline

## Overview
This phase adds video upload and processing capabilities:
- **POST /upload** — Upload video file, extract frames, reconstruct video
- **GET /health/upload** — Health check for upload service
- Uses OpenCV for frame extraction
- Uses FFmpeg for video reconstruction

## What's New

### Backend Changes
- Added `app/services/video_service.py` — VideoProcessor class
- Added `app/routes/upload.py` — Upload and processing endpoints
- Updated `requirements.txt` — Added opencv-python, ffmpeg-python

### File Structure
```
backend/
├── app/
│   ├── services/
│   │   └── video_service.py      # NEW: Video processing logic
│   └── routes/
│       └── upload.py              # NEW: Upload endpoints
├── requirements.txt               # UPDATED: Video dependencies
└── ...existing files...

uploads/                           # NEW: Storage for videos
├── [video files uploaded]
└── output/
    └── [processed videos]
```

## Setup

### 1. Install New Dependencies
```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `opencv-python` — Frame extraction
- `opencv-contrib-python` — Additional OpenCV modules
- `ffmpeg-python` — FFmpeg wrapper

### 2. System Requirements
**FFmpeg must be installed on your system:**

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or using scoop
scoop install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 3. Run Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check for Upload Service
**GET /health/upload**

```bash
curl http://localhost:8000/health/upload
```

Response:
```json
{
  "status": "OK",
  "upload_dir": "uploads",
  "output_dir": "uploads/output",
  "max_file_size_mb": 500
}
```

### Upload and Process Video
**POST /upload**

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/video.mp4"
```

Response:
```json
{
  "status": "success",
  "message": "Video processed successfully",
  "input_file": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.mp4",
  "output_file": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6_processed.mp4",
  "output_path": "uploads/output/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6_processed.mp4",
  "file_size_mb": 45.2,
  "frame_count": 1800,
  "fps": 30.0,
  "resolution": [1920, 1080]
}
```

## How to Test

### Test 1: Using cURL
```bash
# Test with a sample video (you need to have one)
curl -X POST http://localhost:8000/upload \
  -F "file=@sample_video.mp4"
```

### Test 2: Using Python
```python
import requests

# Upload and process video
with open("sample_video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )

print(response.json())
```

### Test 3: Using Postman
1. Open Postman
2. Create new **POST** request to `http://localhost:8000/upload`
3. Go to **Body** tab → Select **form-data**
4. Add key `file` with type **File**
5. Select a video file
6. Click **Send**

### Test 4: Using a Sample Video
Create a simple test video with FFmpeg:
```bash
# Create a 10-second test video (solid color)
ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=10 -f lavfi -i sine=f=1000:d=10 output.mp4

# Then upload it
curl -X POST http://localhost:8000/upload \
  -F "file=@output.mp4"
```

## Storage Structure

### Input Files
```
uploads/
├── a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.mp4
├── b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7.avi
└── ...more uploaded files...
```

### Output Files
```
uploads/output/
├── a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6_processed.mp4
├── b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7_processed.mp4
└── ...more processed files...
```

**Note:** Temporary frame files are stored in system temp directory and cleaned up automatically after processing.

## Processing Pipeline

### Step 1: File Upload
- Upload video file via `POST /upload`
- File saved to `uploads/` with unique UUID filename
- File size validated (max 500 MB)

### Step 2: Frame Extraction
- VideoProcessor reads video using OpenCV
- Extracts all frames as PNG files (lossless)
- Stores in temporary directory
- Captures video metadata: FPS, resolution, frame count

### Step 3: Video Reconstruction
- FFmpeg reads extracted frames
- Encodes as H.264 MP4 video
- Output saved to `uploads/output/`
- Temporary frames deleted automatically

### Step 4: Response
- Returns processing metadata
- Output file path for download
- Video properties (FPS, resolution, frame count)

## Error Handling

### Common Errors and Solutions

**Error: "Invalid file type"**
```
Supported formats: .mp4, .avi, .mov, .mkv, .webm, .flv
```

**Error: "File too large"**
```
Maximum file size: 500 MB
Split larger files or compress before uploading
```

**Error: "FFmpeg error"**
```
Make sure FFmpeg is installed and in your PATH:
ffmpeg -version
```

**Error: "Failed to open video"**
```
Video file may be corrupted or in unsupported format
Try converting with: ffmpeg -i input.mp4 -c:v libx264 output.mp4
```

## Expected Output

### Terminal Output (Backend)
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete

# When video is uploaded:
# INFO:     POST /upload HTTP/1.1" 200 OK
# Processing: extracting frames, reconstructing video...
```

### Processing Time
Depends on video size:
- 10 second video (30 fps, 1080p): ~5-10 seconds
- 1 minute video (30 fps, 1080p): ~30-60 seconds
- Larger videos may take longer

**Note:** FFmpeg uses CPU-intensive compression. Processing time varies by video resolution and codec.

## Supported Video Formats

| Format | Extension | Support |
|--------|-----------|---------|
| MP4    | .mp4      | ✅ Full |
| AVI    | .avi      | ✅ Full |
| MOV    | .mov      | ✅ Full |
| Matroska | .mkv    | ✅ Full |
| WebM   | .webm     | ✅ Full |
| Flash  | .flv      | ✅ Full |

## What's Done
✅ File upload with validation
✅ Frame extraction using OpenCV
✅ Video reconstruction using FFmpeg
✅ Unique filename generation (UUID)
✅ Automatic temporary file cleanup
✅ Error handling and validation
✅ Video metadata capture

## What's NOT Done Yet
❌ Video filters or effects
❌ Subtitle generation
❌ Emoji/sticker overlays
❌ Sound effects
❌ Frontend UI for upload
❌ Background job queue
❌ Progress tracking

## Next Phase
Phase 3 will add cartoon-style filters:
- OpenCV cartoon filter
- Optional upgrade to CartoonGAN/AnimeGAN
- Apply filters to extracted frames before reconstruction
- Updated response with filter metadata

---

**Notes:**
- All temporary files cleaned up automatically
- Unique UUIDs prevent filename conflicts
- System is production-ready for Phase 3
- No video modifications yet (just extract → reconstruct)
