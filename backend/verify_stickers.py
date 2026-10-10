import os
import sys

def verify_pipeline():
    print("=" * 60)
    print("STICKER OVERLAY PIPELINE VERIFIER")
    print("=" * 60)
    
    # 1. Imports
    try:
        from app.services.sticker_service import StickerService
        print("[PASS] StickerService imported successfully.")
    except Exception as e:
        print(f"[FAIL] Error importing StickerService: {e}")
        return

    # 2. Input Setup
    video_path = "uploads/e84c9584-78d4-4681-879d-6deb01d5770b.mp4"
    output_path = "uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_stickers.mp4"
    
    if not os.path.exists(video_path):
        print(f"[FAIL] ERROR: Sample video not found at {video_path}")
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    # 3. Create Service Instance
    service = StickerService()
    
    print("\n--- STAGE 1: STICKER OVERLAY (FFMPEG) ---")
    try:
        result_video = service.apply_stickers(video_path, output_path)
        print(f"[PASS] Stickers applied successfully!")
        print(f"  - Output Video Path: {result_video}")
        print(f"  - File Size: {os.path.getsize(result_video) / (1024**2):.2f} MB")
        
    except Exception as e:
        print(f"[FAIL] ERROR in Sticker Application: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL STAGES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    verify_pipeline()
