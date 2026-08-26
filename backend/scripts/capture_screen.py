import subprocess

adb = r"C:\Users\navit\AppData\Local\Android\Sdk\platform-tools\adb.exe"
target_path = r"C:\Users\navit\.gemini\antigravity-ide\brain\71beee45-5afd-48c5-b4b7-a5abef5c758a\android_screen_final.png"

with open(target_path, "wb") as f:
    subprocess.run([adb, "exec-out", "screencap", "-p"], stdout=f, timeout=10)

print(f"SUCCESS: Captured screen to {target_path}")
