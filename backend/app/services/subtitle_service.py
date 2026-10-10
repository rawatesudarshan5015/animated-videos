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
    """Handles subtitle generation and SRT file creation using OpenAI Whisper."""

    _model = None

    def __init__(self, model_name: str = "tiny"):
        """
        Initialize subtitle service.

        Args:
            model_name: Name of Whisper model to use (tiny, base, small, medium, large)
                       Defaults to "tiny" for fast CPU processing.
        """
        self.model_name = model_name

    def _get_model(self):
        """Lazy load and cache the Whisper model to avoid multiple long loads."""
        if SubtitleService._model is None:
            import whisper
            print(f"Loading Whisper model '{self.model_name}'...")
            SubtitleService._model = whisper.load_model(self.model_name)
        return SubtitleService._model

    def _extract_audio(self, video_path: str, audio_path: str) -> str:
        """
        Extract mono 16kHz WAV audio from a video using FFmpeg.

        Args:
            video_path: Path to input video file
            audio_path: Output temporary WAV audio path

        Returns:
            str: Path to the extracted audio WAV file
        """
        import ffmpeg
        try:
            (
                ffmpeg
                .input(video_path)
                .output(
                    audio_path,
                    acodec='pcm_s16le',
                    ac=1,
                    ar='16000',
                    **{'loglevel': 'error'}
                )
                .overwrite_output()
                .run()
            )
            return audio_path
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error extracting audio: {e.stderr.decode() if e.stderr else str(e)}")

    def generate_subtitles(self, video_path: str, output_srt_path: Optional[str] = None) -> Tuple[str, List[SubtitleEntry]]:
        """
        Generate subtitles for a video file using OpenAI Whisper.

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
            output_srt_path = os.path.join(os.path.dirname(video_path), f"{video_name}_subtitles.srt")

        # Create temporary audio path
        import tempfile
        # Generate temporary unique wav file
        temp_audio = os.path.join(tempfile.gettempdir(), f"temp_audio_{os.getpid()}_{os.urandom(4).hex()}.wav")

        try:
            # 1. Extract audio from video
            self._extract_audio(video_path, temp_audio)

            # 2. Lazy load Whisper model
            model = self._get_model()

            # 3. Transcribe audio using Whisper
            print("Transcribing audio with Whisper...")
            result = model.transcribe(temp_audio, fp16=False)

            # 4. Map Whisper segments to SubtitleEntry format
            subtitles = []
            for i, segment in enumerate(result.get("segments", []), 1):
                entry = SubtitleEntry(
                    index=i,
                    start_time=segment["start"],
                    end_time=segment["end"],
                    text=segment["text"]
                )
                subtitles.append(entry)

            # If no speech was detected, create a default single entry
            if not subtitles:
                subtitles.append(SubtitleEntry(1, 0.0, 3.0, "[No Speech Detected]"))

            # 5. Write SRT file
            self._write_srt_file(subtitles, output_srt_path)

            return output_srt_path, subtitles

        finally:
            # Always clean up temporary audio files
            if os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass

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

    def _escape_windows_path(self, path_str: str) -> str:
        """Normalize and escape Windows path for FFmpeg filters."""
        # Replace backslashes with forward slashes
        p = path_str.replace('\\', '/')
        # Escape colon (e.g. "E:/" -> "E\:/")
        p = p.replace(':', '\\:')
        # Escape single quotes and commas
        p = p.replace("'", "'\\\\''").replace(",", "\\,")
        return p

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

            # Normalize and escape the SRT path for the FFmpeg subtitles filter
            escaped_srt_path = self._escape_windows_path(srt_path)

            # Build FFmpeg command to burn subtitles
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=f"subtitles='{escaped_srt_path}':force_style='FontSize={font_size},PrimaryColour=&H{self._color_to_bgr(font_color)},OutlineColour=&H{self._color_to_bgr(outline_color)},BorderStyle=1'",
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
            raise RuntimeError(f"FFmpeg error during subtitle burning: {e.stderr.decode() if e.stderr else str(e)}")

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