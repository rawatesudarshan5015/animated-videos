import os
import uuid
import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

import yt_dlp

from app.routes.upload import background_process_video, SUPPORTED_FILTERS, OUTPUT_DIR
from app.services.job_manager import job_manager
from app.services.storage_service import storage_service

router = APIRouter()
UPLOAD_DIR = "uploads"
MAX_VIDEO_DURATION = 300  # 5 minutes in seconds

class YouTubeRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    filter_type: str = Field("none", description="Filter to apply")
    generate_subtitles: bool = Field(False, description="Whether to generate subtitles")
    subtitle_font_size: int = Field(24, description="Font size")
    subtitle_font_color: str = Field("white", description="Font color")
    subtitle_outline_color: str = Field("black", description="Outline color")
    add_stickers: bool = Field(False, description="Add stickers")
    add_sfx: bool = Field(False, description="Add SFX")

def download_and_process_youtube(
    job_id: str,
    url: str,
    saved_path: str,
    output_path: str,
    filter_func,
    request: YouTubeRequest
):
    """Background task to download video and then process it."""
    
    def duration_filter(info, *, incomplete):
        duration = info.get('duration')
        if duration is None:
            return None # Accept if duration is unknown before download
        if duration > MAX_VIDEO_DURATION:
            return f'Video is too long (over {MAX_VIDEO_DURATION//60} mins)'
        return None

    # 1. Download video
    ydl_opts = {
        # Prefer H.264 (avc1) to ensure OpenCV can decode it properly, avoiding AV1 decoding errors
        'format': 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': saved_path,
        'noplaylist': True,
        'quiet': True,
        'match_filter': duration_filter
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Video is too long' in error_msg:
            job_manager.mark_failed(job_id, f"Video exceeds the {MAX_VIDEO_DURATION//60} minute limit.")
        else:
            job_manager.mark_failed(job_id, f"Failed to download YouTube video: {error_msg}")
        return
    except Exception as e:
        job_manager.mark_failed(job_id, f"Unknown error downloading video: {str(e)}")
        return

    # 2. Process video (using the existing background processor)
    subtitle_opts = {
        "font_size": request.subtitle_font_size,
        "font_color": request.subtitle_font_color,
        "outline_color": request.subtitle_outline_color,
    }
    
    background_process_video(
        job_id,
        saved_path,
        output_path,
        filter_func,
        request.generate_subtitles,
        subtitle_opts,
        request.add_stickers,
        request.add_sfx
    )

@router.post("/youtube")
async def process_youtube_link(
    request: YouTubeRequest,
    background_tasks: BackgroundTasks
):
    """Download and process a YouTube video."""
    filter_type = request.filter_type.lower()
    if filter_type not in SUPPORTED_FILTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filter type. Supported: {', '.join(SUPPORTED_FILTERS.keys())}"
        )

    unique_id = str(uuid.uuid4())
    saved_filename = f"{unique_id}.mp4"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    output_filename = f"{unique_id}_processed.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Create job
    job_manager.create_job(unique_id)
    
    filter_func = SUPPORTED_FILTERS.get(filter_type)
    
    # Dispatch download & processing task
    background_tasks.add_task(
        download_and_process_youtube,
        unique_id,
        request.url,
        saved_path,
        output_path,
        filter_func,
        request
    )
    
    # Passive cleanup
    background_tasks.add_task(storage_service.cleanup_old_files, max_age_hours=24)

    return {
        "status": "success",
        "message": "YouTube download and processing started",
        "job_id": unique_id
    }
