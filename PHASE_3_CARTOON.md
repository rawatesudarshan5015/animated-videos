# Phase 3: Cartoon Stylization

## Overview
This phase adds cartoon-style filtering to the video processing pipeline:
- **Cartoon filter service** — Multiple filter intensity levels
- **Frame-level filtering** — Applies effects to each extracted frame
- **Filter parameter support** — Choose filter via API query parameter
- **Efficient processing** — Uses OpenCV only (no heavy ML models)

## What's New

### Backend Changes
- Added `app/services/cartoon_filter.py` — CartoonFilter class with multiple filter modes
- Updated `app/services/video_service.py` — Added `apply_filter_to_frames()` method
- Updated `app/routes/upload.py` — Added `filter_type` parameter to `/upload` endpoint

### Available Filters

| Filter | Type | Effect | CPU Cost |
|--------|------|--------|----------|
| `none` | - | No filter applied | Low |
| `cartoon` | Standard | Balanced cartoon effect | Medium |
| `light_cartoon` | Fast | Subtle cartoon look | Low |
| `heavy_cartoon` | Strong | Pronounced cartoon effect | Medium |

## How the Cartoon Filter Works

### Algorithm Steps

1. **Bilateral Filtering**
   - Reduces noise while preserving edges
   - Creates smooth color regions
   - Parameter: kernel size, sigma values

2. **Edge Detection**
   - Uses adaptive thresholding on grayscale image
   - Detects outlines automatically
   - Creates black lines on white background

3. **Edge Dilation**
   - Thickens edges for visibility
   - Makes outlines more pronounced

4. **Color Quantization**
   - Reduces color palette
   - Creates distinct color blocks
   - Gives cartoon-like appearance

5. **Edge Overlay**
   - Combines quantized colors with detected edges
   - Creates final cartoon effect

## Setup

No new dependencies needed. Uses existing OpenCV and FFmpeg.

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Upload Video with Cartoon Filter
**POST /upload?filter_type={filter_type}**

Supported filter types:
- `none` — No filter (default)
- `cartoon` — Standard cartoon effect
- `light_cartoon` — Light cartoon effect (faster)
- `heavy_cartoon` — Heavy cartoon effect (more pronounced)

#### Example 1: Upload with Standard Cartoon Filter
```bash
curl -X POST "http://localhost:8000/upload?filter_type=cartoon" \
  -F "file=@video.mp4"
```

#### Example 2: Upload with Light Cartoon Filter
```bash
curl -X POST "http://localhost:8000/upload?filter_type=light_cartoon" \
  -F "file=@video.mp4"
```

#### Example 3: Upload with Heavy Cartoon Filter
```bash
curl -X POST "http://localhost:8000/upload?filter_type=heavy_cartoon" \
  -F "file=@video.mp4"
```

#### Example 4: Upload with No Filter (default)
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@video.mp4"
```

### Response
```json
{
  "status": "success",
  "message": "Video processed successfully",
  "input_file": "unique-uuid.mp4",
  "output_file": "unique-uuid_processed.mp4",
  "output_path": "uploads/output/unique-uuid_processed.mp4",
  "file_size_mb": 12.5,
  "frame_count": 300,
  "fps": 30.0,
  "resolution": [1280, 720],
  "filter_applied": "cartoon"
}
```

### Health Check
```bash
curl http://localhost:8000/health/upload
```

Response:
```json
{
  "status": "OK",
  "upload_dir": "uploads",
  "output_dir": "uploads/output",
  "max_file_size_mb": 500,
  "supported_filters": ["none", "cartoon", "light_cartoon", "heavy_cartoon"]
}
```

## How to Test

### Test 1: Create Sample Video
```bash
ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=10 -f lavfi -i sine=f=1000:d=10 test.mp4
```

### Test 2: Upload with Cartoon Filter
```bash
curl -X POST "http://localhost:8000/upload?filter_type=cartoon" \
  -F "file=@test.mp4"
```

### Test 3: Upload with Different Filter
```bash
curl -X POST "http://localhost:8000/upload?filter_type=light_cartoon" \
  -F "file=@test.mp4"
```

### Test 4: Using Python
```python
import requests

# Upload with cartoon filter
with open("test.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload?filter_type=cartoon",
        files={"file": f}
    )

result = response.json()
print(f"Filter applied: {result['filter_applied']}")
print(f"Output: {result['output_path']}")
```

### Test 5: Compare Filters (Postman)
1. Upload same video 4 times with different filters:
   - `?filter_type=none`
   - `?filter_type=light_cartoon`
   - `?filter_type=cartoon`
   - `?filter_type=heavy_cartoon`
2. Download output videos
3. Open in video player to compare results

## Processing Pipeline

### Complete Flow
```
Input Video
    ↓
[Phase 2] Extract Frames (OpenCV)
    ↓
[Phase 3] Apply Cartoon Filter (Optional)
    - Bilateral Filter
    - Edge Detection
    - Color Quantization
    - Edge Overlay
    ↓
[Phase 2] Reconstruct Video (FFmpeg)
    ↓
Output Video (with or without cartoon effect)
```

## Performance Characteristics

### Processing Time (approximate)
- 10 sec video (30 fps, 1080p):
  - No filter: ~5-10 seconds
  - Light cartoon: ~8-12 seconds
  - Standard cartoon: ~15-20 seconds
  - Heavy cartoon: ~20-25 seconds

- CPU cost increases with filter intensity
- Larger resolutions take longer
- Processing is single-threaded

### Memory Usage
- Temporary frames stored in system temp directory
- Auto-cleaned after processing
- Memory depends on frame count and resolution

## Filter Details

### Standard Cartoon Filter
- **Bilateral filter kernel:** 9 (adjusts with intensity parameter)
- **Color quantization:** 25-level reduction
- **Edge detection:** Adaptive threshold (mean, blocksize=9)
- **Best for:** General cartoon effect, balanced quality/speed

### Light Cartoon Filter
- **Bilateral filter kernel:** 9
- **Color quantization:** 32-level reduction
- **No edge detection step**
- **Best for:** Fast processing, subtle effect, real-time usage

### Heavy Cartoon Filter
- **Bilateral filter kernel:** 15
- **Color space:** LAB (better color processing)
- **Color quantization:** 20-level reduction
- **Best for:** Strong effect, artistic look, offline processing

## Edge Cases Handled

✅ Frame count validation (ensures all frames extracted)
✅ Resolution mismatch detection
✅ Corrupted frame recovery
✅ Missing frame directory cleanup
✅ Temporary file auto-deletion
✅ Error logging with descriptive messages

## File Storage

### Structure
```
uploads/
├── input videos...
└── output/
    └── processed videos (with cartoon effect)
```

### Cleanup
- Temporary frames: Auto-deleted after processing
- Input videos: Remain in `uploads/`
- Output videos: Remain in `uploads/output/`

## What's Done
✅ Three levels of cartoon filtering
✅ Frame-level filter application
✅ Filter type parameter in API
✅ Edge detection and color quantization
✅ Frame integrity validation
✅ Efficient processing (no ML models)
✅ Error handling and cleanup

## What's NOT Done Yet
❌ Subtitle generation (Phase 4)
❌ Emoji/sticker overlays (Phase 5)
❌ Sound effects (Phase 6)
❌ Frontend UI (Phase 7)
❌ Async job queue (Phase 8)
❌ S3 storage (Phase 9)

## Next Phase
Phase 4 will add subtitle generation:
- OpenAI Whisper for speech-to-text
- Auto-subtitle generation
- Subtitle overlay on video
- Manual subtitle support

---

**Notes:**
- Filters use OpenCV only (no PyTorch/TensorFlow)
- All processing happens in-memory during frame stage
- No multi-processing yet (Phase 8 will add job queue)
- Production-ready for single-file uploads
