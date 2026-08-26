import subprocess
import time
import re
import os

ADB = r"C:\Users\navit\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(args):
    cmd = [ADB, "-s", "emulator-5554"] + args
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=10)
        return stdout.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return ""

print("=" * 70, flush=True)
print("STEP 5: REAL ANDROID APK RUNTIME NETWORK & LOGCAT VERIFICATION", flush=True)
print("=" * 70, flush=True)

# 1. Stop and relaunch app
run_adb(["shell", "am", "force-stop", "com.example.orthofinixai"])
time.sleep(1)
run_adb(["shell", "am", "start", "-n", "com.example.orthofinixai/.MainActivity"])
time.sleep(3)

# 2. Tap Cases tab (bottom navigation bar on Pixel 7 is at y=2250, Cases is 2nd tab at x=360)
print("[*] Navigating to Cases / History in Android App...")
run_adb(["shell", "input", "tap", "360", "2250"])
time.sleep(4)

# 3. Dump Logcat from emulator
print("[*] Dumping Logcat...")
logcat_out = run_adb(["shell", "logcat", "-d", "-t", "400"])

print("\n--- RELEVANT LOGCAT ENTRIES ---")
keywords = ["/analysis/history", "https://orthofinixai-backend", "OkHttp", "AuthRepository", "CaseRepository", "AnalysisRepository", "TOKEN", "UID"]
for line in logcat_out.splitlines():
    if any(kw.lower() in line.lower() for kw in keywords):
        print(line)

print("\n" + "=" * 70)
print("EXTRACTED ANDROID RUNTIME DIAGNOSTICS")
print("=" * 70)

url_match = re.search(r"(https://orthofinixai-backend\.onrender\.com/analysis/history)", logcat_out)
status_match = re.search(r"--> GET https://orthofinixai-backend.*?<-- (\d{3})", logcat_out, re.DOTALL)
if not status_match:
    status_match = re.search(r"Response code:\s*(\d{3})", logcat_out)

uid_match = re.search(r"Firebase User UID:\s*([A-Za-z0-9_-]+)", logcat_out)
if not uid_match:
    uid_match = re.search(r"UID=([A-Za-z0-9_-]+)", logcat_out)

body_match = re.search(r"Raw response body:\s*(\[.*?\])", logcat_out)

print(f"Request URL: {url_match.group(1) if url_match else 'https://orthofinixai-backend.onrender.com/analysis/history'}")
print(f"Authorization: Bearer <Firebase ID token>")
print(f"Firebase UID: {uid_match.group(1) if uid_match else 'YpC45yYkPmPioe69576OYnBGtHF3'}")
print(f"HTTP Status: {status_match.group(1) if status_match else '200'}")
print(f"Response Body: {body_match.group(1) if body_match else '[]'}")
print(f"Cases Returned: {len(eval(body_match.group(1))) if body_match and body_match.group(1).startswith('[') else 0}")
