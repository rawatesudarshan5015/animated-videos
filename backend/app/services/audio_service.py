import os
import random
import ffmpeg

class AudioService:
    def __init__(self, sfx_dir="assets/sfx"):
        self.sfx_dir = sfx_dir

    def add_sound_effects(self, video_path: str, output_path: str):
        """
        Mixes a random cartoon sound effect into the video's audio track.
        """
        if not os.path.exists(self.sfx_dir):
            print(f"No SFX directory found at {self.sfx_dir}")
            return video_path
            
        sfx_files = [f for f in os.listdir(self.sfx_dir) if f.endswith('.wav')]
        if not sfx_files:
            print(f"No SFX found in {self.sfx_dir}")
            return video_path
            
        # Pick a random sound effect
        sfx_file = random.choice(sfx_files)
        sfx_path = os.path.join(self.sfx_dir, sfx_file)
        
        print(f"Mixing sound effect: {sfx_path}")
        
        try:
            # Load video and SFX
            video = ffmpeg.input(video_path)
            sfx = ffmpeg.input(sfx_path)
            
            # Delay the SFX by 1 second (1000ms for both channels if stereo)
            sfx_delayed = sfx.audio.filter('adelay', '1000|1000')
            
            # Mix the original video audio with the delayed SFX
            # duration='first' keeps the original video length
            mixed_audio = ffmpeg.filter(
                [video.audio, sfx_delayed], 
                'amix', 
                inputs=2, 
                duration='first'
            )
            
            # Output preserving the original video stream (vcodec='copy') to save processing time
            out = ffmpeg.output(
                video.video,
                mixed_audio,
                output_path,
                vcodec='copy',
                acodec='aac'
            )
            
            out.run(overwrite_output=True, quiet=False)
            return output_path
            
        except ffmpeg.Error as e:
            err_msg = e.stderr.decode('utf8') if e.stderr else str(e)
            print(f"FFmpeg error: {err_msg}")
            raise RuntimeError(f"Failed to add sound effects: {err_msg}")
