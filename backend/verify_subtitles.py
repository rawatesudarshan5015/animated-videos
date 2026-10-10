import os
import sys

def verify_pipeline():
    print("=" * 60)
    print("SUBTITLE & WHISPER PIPELINE VERIFIER")
    print("=" * 60)
    
    # 1. Imports
    try:
        from app.services.subtitle_service import SubtitleService
        print("[PASS] SubtitleService imported successfully.")
    except Exception as e:
        print(f"[FAIL] Error importing SubtitleService: {e}")
        return

    # Check if whisper is installed
    try:
        import whisper
        print("[PASS] whisper library is installed and available.")
    except ImportError:
        print("[FAIL] ERROR: whisper library is not installed yet. Please wait for the background pip task to finish!")
        return

    # 2. Input Setup
    video_path = "uploads/e84c9584-78d4-4681-879d-6deb01d5770b.mp4"
    srt_path = "uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_subtitles.srt"
    subtitled_video_path = "uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_subtitled.mp4"
    
    if not os.path.exists(video_path):
        print(f"[FAIL] ERROR: Sample video not found at {video_path}")
        return

    # Remove pre-existing outputs to prevent false positives
    for p in [srt_path, subtitled_video_path]:
        if os.path.exists(p):
            os.remove(p)

    # 3. Create Service Instance (using tiny model for fast execution)
    service = SubtitleService(model_name="tiny")
    
    print("\n--- STAGE 1: SUBTITLE GENERATION (WHISPER) ---")
    try:
        generated_srt, entries = service.generate_subtitles(video_path, srt_path)
        print(f"[PASS] Subtitles generated successfully!")
        print(f"  - Output SRT Path: {generated_srt}")
        print(f"  - Transcribed Entries Count: {len(entries)}")
        print(f"  - First Subtitle: {entries[0].text if entries else '[None]'}")
        
        # Display first 3 subtitle entries
        print("\nFirst few SRT entries:")
        with open(generated_srt, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print("".join(lines[:12]))
            
    except Exception as e:
        print(f"[FAIL] ERROR in Subtitle Generation: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- STAGE 2: SUBTITLE BURNING (FFMPEG) ---")
    try:
        result_video = service.burn_subtitles_into_video(
            video_path=video_path,
            srt_path=generated_srt,
            output_path=subtitled_video_path,
            font_size=28,
            font_color="yellow",  # Test BGR conversion
            outline_color="black"
        )
        print(f"[PASS] Subtitles burned successfully!")
        print(f"  - Output Video Path: {result_video}")
        print(f"  - File Size: {os.path.getsize(result_video) / (1024**2):.2f} MB")
        
    except Exception as e:
        print(f"[FAIL] ERROR in Subtitle Burning: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL STAGES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    verify_pipeline()
