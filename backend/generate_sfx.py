import os
import wave
import math
import struct

def generate_boing_sfx(filepath, duration=0.5, sample_rate=44100):
    """
    Generates a cartoon 'boing' or 'pop' sound effect using a swept sine wave
    (frequency sweeping upwards).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Audio parameters
    start_freq = 200.0  # Hz
    end_freq = 800.0    # Hz
    amplitude = 16000   # Max 32767 for 16-bit
    
    with wave.open(filepath, 'w') as wav_file:
        n_channels = 1
        sampwidth = 2
        
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        
        num_frames = int(duration * sample_rate)
        
        for i in range(num_frames):
            t = float(i) / sample_rate
            
            # Swept frequency: linear sweep from start_freq to end_freq
            current_freq = start_freq + (end_freq - start_freq) * (t / duration)
            
            # Calculate wave value
            value = int(amplitude * math.sin(2.0 * math.pi * current_freq * t))
            
            # Add an envelope (fade out) so it doesn't clip abruptly
            envelope = 1.0 - (t / duration)
            value = int(value * envelope)
            
            # Pack as 16-bit little-endian
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
            
    print(f"Generated sound effect: {filepath}")

if __name__ == "__main__":
    generate_boing_sfx("assets/sfx/boing.wav")
