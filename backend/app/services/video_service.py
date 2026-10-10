"""
Video processing service for extracting frames and reconstructing videos.
Handles video I/O operations using OpenCV and FFmpeg.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Optional

import cv2
import ffmpeg


class VideoProcessor:
    """Handles video frame extraction and reconstruction."""

    def __init__(self, temp_dir: str = None):
        """
        Initialize video processor.
        
        Args:
            temp_dir: Optional temporary directory for frame storage.
                     If None, creates a new temp directory for each operation.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def extract_frames(self, video_path: str, output_dir: str) -> dict:
        """
        Extract frames from video using OpenCV.
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save extracted frames
            
        Returns:
            dict with extraction metadata:
                - frame_count: number of frames extracted
                - fps: frames per second
                - resolution: tuple of (width, height)
                - frame_dir: directory where frames are stored
                
        Raises:
            FileNotFoundError: if video file doesn't exist
            RuntimeError: if frame extraction fails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")

        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if fps == 0 or frame_count == 0:
                raise RuntimeError("Invalid video properties: FPS or frame count is 0")

            # Extract frames
            frame_index = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Save frame as PNG (lossless)
                frame_path = os.path.join(output_dir, f"frame_{frame_index:06d}.png")
                cv2.imwrite(frame_path, frame)
                frame_index += 1

            return {
                "frame_count": frame_count,
                "fps": fps,
                "resolution": (width, height),
                "frame_dir": output_dir,
            }

        finally:
            cap.release()

    def reconstruct_video(
        self, 
        frame_dir: str, 
        output_path: str, 
        fps: float, 
        resolution: tuple,
        original_video_path: Optional[str] = None
    ) -> str:
        """
        Reconstruct video from extracted frames using FFmpeg, copying audio from original video.
        
        Args:
            frame_dir: Directory containing extracted frames
            output_path: Path for output video file
            fps: Frames per second for output video
            resolution: Tuple of (width, height)
            original_video_path: Path to original video to extract audio from
            
        Returns:
            str: Path to reconstructed video
            
        Raises:
            RuntimeError: if video reconstruction fails
        """
        if not os.path.exists(frame_dir):
            raise FileNotFoundError(f"Frame directory not found: {frame_dir}")

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Build frame input pattern
            frame_pattern = os.path.join(frame_dir, "frame_%06d.png")

            # Video input stream (from frames)
            video_input = ffmpeg.input(frame_pattern, framerate=fps)

            # If original video is provided, copy its audio
            if original_video_path and os.path.exists(original_video_path):
                audio_input = ffmpeg.input(original_video_path)
                
                # Combine video stream from frames and audio stream from original
                # Use vcodec='libx264', acodec='copy' to preserve original audio quality
                (
                    ffmpeg
                    .output(
                        video_input.video,
                        audio_input.audio,
                        output_path,
                        vcodec='libx264',
                        pix_fmt='yuv420p',
                        acodec='copy',
                        **{'loglevel': 'error'}
                    )
                    .overwrite_output()
                    .run()
                )
            else:
                # Reconstruct video without audio (fallback)
                (
                    ffmpeg
                    .output(
                        video_input,
                        output_path,
                        vcodec='libx264',
                        pix_fmt='yuv420p',
                        **{'loglevel': 'error'}
                    )
                    .overwrite_output()
                    .run()
                )

            if not os.path.exists(output_path):
                raise RuntimeError("FFmpeg failed to create output video")

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during video reconstruction: {e.stderr.decode()}")

    def apply_filter_to_frames(
        self, 
        frame_dir: str, 
        filter_func: Callable, 
        output_dir: Optional[str] = None
    ) -> str:
        """
        Apply a filter function to all frames in a directory.
        
        Args:
            frame_dir: Directory containing frame PNG files
            filter_func: Function that takes a frame (np.ndarray) and returns filtered frame
            output_dir: Optional directory for filtered frames. If None, modifies in-place
            
        Returns:
            str: Directory containing filtered frames
            
        Raises:
            FileNotFoundError: if frame directory doesn't exist
            RuntimeError: if frame processing fails
        """
        if not os.path.exists(frame_dir):
            raise FileNotFoundError(f"Frame directory not found: {frame_dir}")

        # Use output directory if provided, otherwise modify in-place
        target_dir = output_dir if output_dir else frame_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Get all frame files sorted by number
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.startswith("frame_")])
        
        if not frame_files:
            raise RuntimeError(f"No frame files found in {frame_dir}")

        try:
            for i, frame_file in enumerate(frame_files):
                frame_path = os.path.join(frame_dir, frame_file)
                
                # Read frame
                frame = cv2.imread(frame_path)
                if frame is None:
                    raise RuntimeError(f"Failed to read frame: {frame_path}")

                # Apply filter
                filtered_frame = filter_func(frame)

                # Save filtered frame
                if output_dir:
                    output_path = os.path.join(output_dir, frame_file)
                else:
                    output_path = frame_path

                success = cv2.imwrite(output_path, filtered_frame)
                if not success:
                    raise RuntimeError(f"Failed to write filtered frame: {output_path}")

        except Exception as e:
            raise RuntimeError(f"Error applying filter to frames: {str(e)}")

        return target_dir

    def process_video(
        self, 
        video_path: str, 
        output_path: str, 
        filter_func: Optional[Callable] = None,
        generate_subtitles: bool = False,
        subtitle_options: Optional[dict] = None,
        add_stickers: bool = False,
        add_sfx: bool = False
    ) -> dict:
        """
        Complete video processing pipeline: extract frames, optionally filter, optionally add subtitles, and reconstruct.
        
        Args:
            video_path: Path to input video
            output_path: Path for output video
            filter_func: Optional function to apply to each frame.
                        Function signature: frame (np.ndarray) -> filtered_frame (np.ndarray)
            generate_subtitles: Whether to generate and burn subtitles into the video
            subtitle_options: Optional dict with subtitle settings:
                            - font_size: Font size (default 24)
                            - font_color: Font color (default "white")
                            - outline_color: Outline color (default "black")
            add_stickers: Whether to add sticker overlays to the video
            add_sfx: Whether to add sound effects to the video
            
        Returns:
            dict with processing results
            
        Raises:
            Various exceptions from extract_frames, apply_filter_to_frames, and reconstruct_video
        """
        # Create temporary directory for frames
        frames_temp_dir = os.path.join(self.temp_dir, f"frames_{os.getpid()}")
        
        try:
            # Step 1: Extract frames
            extraction_info = self.extract_frames(video_path, frames_temp_dir)

            # Step 2: Apply filter if provided
            filtered_frames_dir = frames_temp_dir
            filter_applied = False
            if filter_func:
                self.apply_filter_to_frames(frames_temp_dir, filter_func)
                filter_applied = True

            # Step 3: Reconstruct video (temporary if subtitles, stickers, or sfx needed)
            temp_video_path = output_path
            if generate_subtitles or add_stickers or add_sfx:
                # Create intermediate video
                temp_video_path = output_path.replace('.mp4', '_temp.mp4')
            
            self.reconstruct_video(
                filtered_frames_dir,
                temp_video_path,
                extraction_info["fps"],
                extraction_info["resolution"],
                original_video_path=video_path
            )

            # Step 4: Generate and burn subtitles if requested
            subtitles_generated = False
            srt_path = None
            if generate_subtitles:
                from app.services.subtitle_service import SubtitleService
                
                subtitle_service = SubtitleService()
                
                # Generate subtitles
                video_name = Path(video_path).stem
                srt_path = os.path.join(os.path.dirname(output_path), f"{video_name}_subtitles.srt")
                srt_path, subtitle_entries = subtitle_service.generate_subtitles(video_path, srt_path)
                
                # Target path for subtitles depends on whether stickers or sfx are added next
                subtitle_target = output_path.replace('.mp4', '_subbed.mp4') if (add_stickers or add_sfx) else output_path
                
                # Burn subtitles into video
                subtitle_opts = subtitle_options or {}
                subtitle_service.burn_subtitles_into_video(
                    temp_video_path,
                    srt_path,
                    subtitle_target,
                    font_size=subtitle_opts.get('font_size', 24),
                    font_color=subtitle_opts.get('font_color', 'white'),
                    outline_color=subtitle_opts.get('outline_color', 'black')
                )
                
                # Clean up initial temp_video_path
                if os.path.exists(temp_video_path) and temp_video_path != output_path:
                    os.remove(temp_video_path)
                    
                temp_video_path = subtitle_target
                subtitles_generated = True

            # Step 5: Add stickers if requested
            stickers_added = False
            if add_stickers:
                from app.services.sticker_service import StickerService
                sticker_service = StickerService()
                
                sticker_target = output_path.replace('.mp4', '_stickered.mp4') if add_sfx else output_path
                sticker_service.apply_stickers(temp_video_path, sticker_target)
                
                # Clean up the previous temp video
                if os.path.exists(temp_video_path) and temp_video_path != output_path:
                    os.remove(temp_video_path)
                    
                temp_video_path = sticker_target
                stickers_added = True

            # Step 6: Add sound effects if requested
            sfx_added = False
            if add_sfx:
                from app.services.audio_service import AudioService
                audio_service = AudioService()
                
                audio_service.add_sound_effects(temp_video_path, output_path)
                
                if os.path.exists(temp_video_path) and temp_video_path != output_path:
                    os.remove(temp_video_path)
                
                sfx_added = True

            return {
                "status": "success",
                "output": output_path,
                "frame_count": extraction_info["frame_count"],
                "fps": extraction_info["fps"],
                "resolution": extraction_info["resolution"],
                "filter_applied": filter_applied,
                "subtitles_generated": subtitles_generated,
                "srt_path": srt_path,
                "stickers_added": stickers_added,
                "sfx_added": sfx_added,
            }

        finally:
            # Clean up temporary frames directory
            if os.path.exists(frames_temp_dir):
                shutil.rmtree(frames_temp_dir)
