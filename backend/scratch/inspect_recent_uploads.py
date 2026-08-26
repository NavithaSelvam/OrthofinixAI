import os
import time

def inspect():
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("Uploads dir not found")
        return
        
    files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.endswith(".jpg")]
    files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"Total uploaded files: {len(files)}")
    print("Most recent 15 files:")
    for f in files[:15]:
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(f)))
        size = os.path.getsize(f)
        print(f"File: {f}, Size: {size} bytes, Time: {mtime}")

if __name__ == "__main__":
    inspect()
