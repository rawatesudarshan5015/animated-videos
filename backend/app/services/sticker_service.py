import os
import random
import ffmpeg

class StickerService:
    def __init__(self, stickers_dir="assets/stickers"):
        self.stickers_dir = stickers_dir

    def apply_stickers(self, video_path: str, output_path: str):
        """
        Applies a random sticker from the assets directory to the video as an overlay.
        """
        if not os.path.exists(self.stickers_dir):
            print(f"No stickers directory found at {self.stickers_dir}")
            return video_path
            
        stickers = [f for f in os.listdir(self.stickers_dir) if f.endswith('.png')]
        if not stickers:
            print(f"No stickers found in {self.stickers_dir}")
            return video_path
            
        # Pick a random sticker for this video
        sticker_file = random.choice(stickers)
        sticker_path = os.path.join(self.stickers_dir, sticker_file)
        
        print(f"Applying sticker overlay: {sticker_path}")
        
        try:
            # Load video and image inputs
            video = ffmpeg.input(video_path)
            sticker = ffmpeg.input(sticker_path)
            
            # Apply overlay: top right corner with 20px padding
            # x = W-w-20, y = 20
            # To handle videos with and without audio properly, we can map both streams.
            # However, if audio is guaranteed, `video.audio` is fine.
            # Using vcodec='libx264' to ensure broad compatibility.
            
            stream = ffmpeg.overlay(video.video, sticker, x='W-w-40', y='40')
            
            # Include audio from the original video
            out = ffmpeg.output(
                stream, 
                video.audio, 
                output_path,
                vcodec='libx264',
                acodec='aac'
            )
            
            out.run(overwrite_output=True, quiet=False)
            return output_path
            
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode('utf8') if e.stderr else str(e)
            print(f"FFmpeg error: {err_msg}")
            raise RuntimeError(f"Failed to apply stickers: {err_msg}")
