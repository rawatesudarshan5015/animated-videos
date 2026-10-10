"""
Upload and video processing routes.
Handles video file uploads and initiates processing pipeline with optional filters.
"""
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, BackgroundTasks

from app.services.video_service import VideoProcessor
from app.services.cartoon_filter import CartoonFilter
from app.services.job_manager import job_manager
from app.services.storage_service import storage_service

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads"
OUTPUT_DIR = os.path.join(UPLOAD_DIR, "output")
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Supported filters
SUPPORTED_FILTERS = {
    "none": None,
    "cartoon": CartoonFilter.apply_cartoon_filter,
    "light_cartoon": CartoonFilter.apply_light_cartoon,
    "heavy_cartoon": CartoonFilter.apply_heavy_cartoon,
}


def background_process_video(
    job_id: str,
    saved_path: str,
    output_path: str,
    filter_func,
    generate_subtitles: bool,
    subtitle_options: dict,
    add_stickers: bool,
    add_sfx: bool
):
    try:
        processor = VideoProcessor()
        result = processor.process_video(
            saved_path,
            output_path,
            filter_func,
            generate_subtitles=generate_subtitles,
            subtitle_options=subtitle_options,
            add_stickers=add_stickers,
            add_sfx=add_sfx
        )
        job_manager.mark_completed(job_id, result)
        
        # Aggressively clean up intermediate files to save disk space
        if os.path.exists(saved_path):
            os.remove(saved_path)
            
        if result.get("srt_path") and os.path.exists(result["srt_path"]):
            os.remove(result["srt_path"])
            
    except Exception as e:
        job_manager.mark_failed(job_id, str(e))
        # Even on failure, try to clean up the original upload
        if os.path.exists(saved_path):
            os.remove(saved_path)


@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    filter_type: str = Query("none", description="Filter to apply: none, cartoon, light_cartoon, heavy_cartoon"),
    generate_subtitles: bool = Query(False, description="Whether to generate and burn subtitles into the video"),
    subtitle_font_size: int = Query(24, description="Font size for subtitles"),
    subtitle_font_color: str = Query("white", description="Font color for subtitles"),
    subtitle_outline_color: str = Query("black", description="Outline color for subtitles"),
    add_stickers: bool = Query(False, description="Whether to add kid-friendly sticker overlays"),
    add_sfx: bool = Query(False, description="Whether to add funny sound effects")
):
    """
    Upload and process a video file with optional cartoon filter.
    
    - Saves video to uploads/ directory
    - Extracts frames using OpenCV
    - Optionally applies cartoon filter to frames
    - Reconstructs video using FFmpeg
    - Returns output video path and metadata
    
    Args:
        file: Video file to upload
        filter_type: Type of filter to apply (none, cartoon, light_cartoon, heavy_cartoon)
        
    Returns:
        dict with processing results
        
    Raises:
        HTTPException 400: Invalid file type, size, or filter
        HTTPException 500: Processing error
    """
    # Validate filter type
    filter_type = filter_type.lower()
    if filter_type not in SUPPORTED_FILTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filter type. Supported: {', '.join(SUPPORTED_FILTERS.keys())}"
        )

    # Validate file type
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )

    # Generate unique filename
    unique_id = str(uuid.uuid4())
    saved_filename = f"{unique_id}{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    try:
        # Save uploaded file
        file_size = 0
        with open(saved_path, "wb") as buffer:
            while True:
                chunk = await file.read(8192)  # Read in 8KB chunks
                if not chunk:
                    break
                file_size += len(chunk)
                
                # Check file size limit
                if file_size > MAX_FILE_SIZE:
                    os.remove(saved_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024**2):.0f} MB"
                    )
                
                buffer.write(chunk)

        # Create job
        job_manager.create_job(unique_id)
        
        output_filename = f"{unique_id}_processed.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Get filter function if specified
        filter_func = SUPPORTED_FILTERS.get(filter_type)

        # Dispatch background task
        background_tasks.add_task(
            background_process_video,
            unique_id,
            saved_path,
            output_path,
            filter_func,
            generate_subtitles,
            {
                "font_size": subtitle_font_size,
                "font_color": subtitle_font_color,
                "outline_color": subtitle_outline_color,
            },
            add_stickers,
            add_sfx
        )

        # Dispatch background cleanup of old files (passive cleanup)
        background_tasks.add_task(storage_service.cleanup_old_files, max_age_hours=24)

        return {
            "status": "success",
            "message": "Video uploaded and processing started",
            "job_id": unique_id
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Clean up on error
        if os.path.exists(saved_path):
            os.remove(saved_path)

        raise HTTPException(
            status_code=500,
            detail=f"Error starting video processing: {str(e)}"
        )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the processing status of a video job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/health/upload")
async def upload_health():
    """Health check for upload service."""
    return {
        "status": "OK",
        "upload_dir": UPLOAD_DIR,
        "output_dir": OUTPUT_DIR,
        "max_file_size_mb": MAX_FILE_SIZE / (1024**2),
        "supported_filters": list(SUPPORTED_FILTERS.keys()),
    }
