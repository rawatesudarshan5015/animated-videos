import os
import sys

def verify_pipeline():
    print("=" * 60)
    print("SOUND EFFECT PIPELINE VERIFIER")
    print("=" * 60)
    
    # 1. Imports
    try:
        from app.services.audio_service import AudioService
        print("[PASS] AudioService imported successfully.")
    except Exception as e:
        print(f"[FAIL] Error importing AudioService: {e}")
        return

    # 2. Input Setup
    video_path = "uploads/e84c9584-78d4-4681-879d-6deb01d5770b.mp4"
    output_path = "uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_sfx.mp4"
    
    if not os.path.exists(video_path):
        print(f"[FAIL] ERROR: Sample video not found at {video_path}")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    # 3. Create Service Instance
    service = AudioService()
    
    print("\n--- STAGE 1: SOUND EFFECT MIXING (FFMPEG) ---")
    try:
        result_video = service.add_sound_effects(video_path, output_path)
        print(f"[PASS] Sound effect mixed successfully!")
        print(f"  - Output Video Path: {result_video}")
        print(f"  - File Size: {os.path.getsize(result_video) / (1024**2):.2f} MB")
        
    except Exception as e:
        print(f"[FAIL] ERROR in Sound Mixing: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL STAGES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    verify_pipeline()
