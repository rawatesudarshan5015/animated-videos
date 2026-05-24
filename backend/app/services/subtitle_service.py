"""
Subtitle generation service for video processing.
Uses Whisper for speech-to-text and generates SRT files.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional
import json


class SubtitleEntry:
    """Represents a single subtitle entry."""

    def __init__(self, index: int, start_time: float, end_time: float, text: str):
        """
        Initialize subtitle entry.

        Args:
            index: Subtitle sequence number
            start_time: Start time in seconds
            end_time: End time in seconds
            text: Subtitle text
        """
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text.strip()

    def to_srt_format(self) -> str:
        """
        Convert to SRT format.

        Returns:
            SRT formatted string for this entry
        """
        # Convert seconds to HH:MM:SS,mmm format
        start = self._seconds_to_srt_time(self.start_time)
        end = self._seconds_to_srt_time(self.end_time)

        return f"{self.index}\n{start} --> {end}\n{self.text}\n\n"

    @staticmethod
    def _seconds_to_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class SubtitleService:
    """Handles subtitle generation and SRT file creation."""

    def __init__(self):
        """Initialize subtitle service."""
        # For now, we'll use a mock implementation
        # TODO: Replace with actual Whisper integration
        pass

    def generate_subtitles(self, video_path: str, output_srt_path: Optional[str] = None) -> Tuple[str, List[SubtitleEntry]]:
        """
        Generate subtitles for a video file.

        For now, this is a mock implementation that creates sample subtitles.
        In production, this would use Whisper or similar STT service.

        Args:
            video_path: Path to input video file
            output_srt_path: Optional path to save SRT file. If None, saves alongside video.

        Returns:
            Tuple of (srt_file_path, list of subtitle entries)

        Raises:
            FileNotFoundError: if video file doesn't exist
            RuntimeError: if subtitle generation fails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Generate default SRT path if not provided
        if output_srt_path is None:
            video_name = Path(video_path).stem
            output_srt_path = f"{video_name}_subtitles.srt"

        # Mock subtitle generation
        # In a real implementation, this would:
        # 1. Extract audio from video
        # 2. Run Whisper STT on audio
        # 3. Generate timestamps and text
        subtitles = self._generate_mock_subtitles(video_path)

        # Write SRT file
        self._write_srt_file(subtitles, output_srt_path)

        return output_srt_path, subtitles

    def _generate_mock_subtitles(self, video_path: str) -> List[SubtitleEntry]:
        """
        Generate mock subtitles for demonstration.

        This creates sample subtitles at regular intervals.
        In production, replace with actual Whisper processing.
        """
        # Mock subtitles - in real implementation, this would come from Whisper
        mock_entries = [
            SubtitleEntry(1, 0.0, 3.0, "Welcome to the Kids Video Enhancer!"),
            SubtitleEntry(2, 3.5, 6.5, "This video has been processed with cartoon effects."),
            SubtitleEntry(3, 7.0, 10.0, "Enjoy the enhanced visual experience!"),
            SubtitleEntry(4, 10.5, 13.5, "Created with OpenCV and FFmpeg."),
            SubtitleEntry(5, 14.0, 17.0, "Thank you for using our service!"),
        ]

        return mock_entries

    def _write_srt_file(self, subtitles: List[SubtitleEntry], output_path: str) -> None:
        """
        Write subtitle entries to SRT file.

        Args:
            subtitles: List of subtitle entries
            output_path: Path to output SRT file
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for subtitle in subtitles:
                f.write(subtitle.to_srt_format())

    def burn_subtitles_into_video(
        self,
        video_path: str,
        srt_path: str,
        output_path: str,
        font_size: int = 24,
        font_color: str = "white",
        outline_color: str = "black"
    ) -> str:
        """
        Burn subtitles into video using FFmpeg.

        Args:
            video_path: Path to input video
            srt_path: Path to SRT subtitle file
            output_path: Path for output video with subtitles
            font_size: Font size for subtitles
            font_color: Font color (e.g., "white", "yellow")
            outline_color: Outline color for text

        Returns:
            Path to output video with subtitles

        Raises:
            RuntimeError: if subtitle burning fails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            import ffmpeg

            # Build FFmpeg command to burn subtitles
            # Using subtitles filter to overlay SRT on video
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=f"subtitles={srt_path}:force_style='FontSize={font_size},PrimaryColour=&H{self._color_to_bgr(font_color)},OutlineColour=&H{self._color_to_bgr(outline_color)},BorderStyle=1'",
                    vcodec='libx264',
                    acodec='aac',
                    **{'loglevel': 'error'}
                )
                .overwrite_output()
                .run()
            )

            if not os.path.exists(output_path):
                raise RuntimeError("FFmpeg failed to create subtitled video")

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during subtitle burning: {e.stderr.decode()}")

    def _color_to_bgr(self, color_name: str) -> str:
        """
        Convert color name to BGR hex format for FFmpeg.

        Args:
            color_name: Color name (white, black, yellow, etc.)

        Returns:
            BGR hex string for FFmpeg
        """
        color_map = {
            'white': 'FFFFFF',
            'black': '000000',
            'yellow': '00FFFF',
            'red': '0000FF',
            'blue': 'FF0000',
            'green': '00FF00',
        }

        return color_map.get(color_name.lower(), 'FFFFFF')  # Default to white