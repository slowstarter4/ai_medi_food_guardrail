import os
import shutil

def cleanup():
    count = 0
    for root, dirs, files in os.walk(".", topdown=False):
        for name in dirs:
            if name == "__pycache__" or name == ".pytest_cache":
                full_path = os.path.join(root, name)
                try:
                    shutil.rmtree(full_path)
                    print(f"Deleted: {full_path}")
                    count += 1
                except Exception as e:
                    print(f"Error deleting {full_path}: {e}")
    print(f"\nTotal {count} cache directories deleted.")

if __name__ == "__main__":
    cleanup()
