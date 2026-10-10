import os
import time
from app.services.storage_service import storage_service

def verify_cleanup():
    print("=" * 60)
    print("STORAGE CLEANUP VERIFIER")
    print("=" * 60)
    
    upload_dir = "uploads"
    output_dir = os.path.join(upload_dir, "output")
    
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a fresh file (0 hours old)
    fresh_file = os.path.join(upload_dir, "fresh_dummy.mp4")
    with open(fresh_file, 'w') as f:
        f.write("fresh")
        
    # Create an old file in uploads (48 hours old)
    old_upload = os.path.join(upload_dir, "old_upload_dummy.mp4")
    with open(old_upload, 'w') as f:
        f.write("old")
    # Change modification time to 48 hours ago
    past_time = time.time() - (48 * 3600)
    os.utime(old_upload, (past_time, past_time))
    
    # Create an old file in output (48 hours old)
    old_output = os.path.join(output_dir, "old_output_dummy.mp4")
    with open(old_output, 'w') as f:
        f.write("old")
    os.utime(old_output, (past_time, past_time))
    
    print("\n--- STAGE 1: FILES CREATED ---")
    print(f"Fresh file exists: {os.path.exists(fresh_file)}")
    print(f"Old upload exists: {os.path.exists(old_upload)}")
    print(f"Old output exists: {os.path.exists(old_output)}")
    
    print("\n--- STAGE 2: RUNNING CLEANUP ---")
    storage_service.cleanup_old_files(max_age_hours=24)
    
    print("\n--- STAGE 3: VERIFICATION ---")
    fresh_exists = os.path.exists(fresh_file)
    old_upload_deleted = not os.path.exists(old_upload)
    old_output_deleted = not os.path.exists(old_output)
    
    print(f"Fresh file kept: {'[PASS]' if fresh_exists else '[FAIL]'}")
    print(f"Old upload deleted: {'[PASS]' if old_upload_deleted else '[FAIL]'}")
    print(f"Old output deleted: {'[PASS]' if old_output_deleted else '[FAIL]'}")
    
    if fresh_exists and old_upload_deleted and old_output_deleted:
        print("\n" + "=" * 60)
        print("[SUCCESS] STORAGE CLEANUP PASSED!")
        print("=" * 60)
    else:
        print("\n[FAIL] STORAGE CLEANUP FAILED.")
        
    # Final cleanup of the fresh file
    if os.path.exists(fresh_file):
        os.remove(fresh_file)

if __name__ == "__main__":
    verify_cleanup()
