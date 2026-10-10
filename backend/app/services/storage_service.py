import os
import time

class StorageService:
    def __init__(self, base_dir="uploads"):
        self.base_dir = base_dir

    def cleanup_old_files(self, max_age_hours=24):
        """
        Recursively scans the base directory and deletes any files older than max_age_hours.
        """
        print(f"Running automated storage cleanup. Max age: {max_age_hours} hours")
        if not os.path.exists(self.base_dir):
            return

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                # Don't delete placeholder or dot files
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    # Get file modification time
                    file_mtime = os.path.getmtime(file_path)
                    
                    if (current_time - file_mtime) > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"Deleted old file: {file_path}")
                except Exception as e:
                    print(f"Failed to check/delete {file_path}: {e}")
        
        print(f"Cleanup finished. Removed {deleted_count} old files.")

# Singleton instance
storage_service = StorageService()
