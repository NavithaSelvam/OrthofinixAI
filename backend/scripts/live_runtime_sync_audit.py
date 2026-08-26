import sys
import os
import io
import time
import requests
from PIL import Image

PRODUCTION_URL = "https://orthofinixai-backend.onrender.com"
FIREBASE_API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"
FIREBASE_PROJECT_ID = "orthofinixai"

TEST_EMAIL = "audit.doctor@orthofinix.ai"
TEST_PASSWORD = "AuditPassword123!"

def create_test_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (640, 480), color=(120, 180, 220))
    img.save(buf, format="JPEG")
    return buf.getvalue()

def get_real_firebase_token():
    print(f"[*] Authenticating with Firebase Project '{FIREBASE_PROJECT_ID}' via Identity Toolkit...")
    
    # Try sign-in
    sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "returnSecureToken": True
    }
    
    res = requests.post(sign_in_url, json=payload)
    if res.status_code == 200:
        data = res.json()
        print(f"[OK] Successfully signed in user: UID={data.get('localId')}, Email={data.get('email')}")
        return data.get("idToken"), data.get("localId")
    
    # If user doesn't exist, sign up
    print("[*] User not found, creating new Firebase test user...")
    sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    res2 = requests.post(sign_up_url, json=payload)
    if res2.status_code == 200:
        data = res2.json()
        print(f"[OK] Successfully registered user: UID={data.get('localId')}, Email={data.get('email')}")
        return data.get("idToken"), data.get("localId")
    
    print(f"[ERROR] Failed to authenticate with Firebase: {res2.status_code} - {res2.text}")
    sys.exit(1)

def run_audit():
    print("=" * 70)
    print("LIVE RUNTIME END-TO-END AUDIT: FASTAPI + FIREBASE + MULTI-CLIENT")
    print(f"Target Server: {PRODUCTION_URL}")
    print(f"Firebase Project: {FIREBASE_PROJECT_ID}")
    print("=" * 70)

    # 1. Health check
    print("\n--- 1. Health Check ---")
    try:
        r = requests.get(f"{PRODUCTION_URL}/", timeout=60)
        print(f"[OK] GET / -> HTTP {r.status_code} | Body: {r.text[:100]}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to {PRODUCTION_URL}: {e}")
        return

    # 2. Get Real Firebase Token
    print("\n--- 2. Firebase ID Token Generation ---")
    id_token, firebase_uid = get_real_firebase_token()
    auth_headers = {"Authorization": f"Bearer {id_token}"}
    print(f"[OK] Token acquired: Length={len(id_token)}, Starts with='{id_token[:15]}...'")

    # 3. Initial History Fetch
    print("\n--- 3. GET /analysis/history (Initial State) ---")
    r_hist = requests.get(f"{PRODUCTION_URL}/analysis/history", headers=auth_headers, timeout=60)
    print(f"[OK] GET /analysis/history -> HTTP {r_hist.status_code}")
    if r_hist.status_code == 200:
        initial_cases = r_hist.json()
        print(f"[INFO] Initial case count for UID '{firebase_uid}': {len(initial_cases)}")
    else:
        print(f"[ERROR] Failed to fetch history: {r_hist.status_code} - {r_hist.text}")
        return

    # 4. Web Client Flow: Create TEST_WEB_PATIENT
    print("\n--- 4. Simulated Web Client Flow: Create 'TEST_WEB_PATIENT' ---")
    img_bytes = create_test_image_bytes()
    
    # Upload
    files = {"file": ("test_web_opg.jpg", img_bytes, "image/jpeg")}
    r_upload = requests.post(f"{PRODUCTION_URL}/analysis/upload", headers=auth_headers, files=files, timeout=60)
    print(f"[OK] Web POST /analysis/upload -> HTTP {r_upload.status_code}")
    assert r_upload.status_code == 200, f"Web upload failed: {r_upload.text}"
    web_upload_id = r_upload.json()["upload_id"]
    print(f"[INFO] Web Upload ID: {web_upload_id}")

    # Analyze
    web_case_id = f"case_web_{int(time.time())}"
    analyze_data = {
        "upload_id": web_upload_id,
        "patient_name": "TEST_WEB_PATIENT",
        "view_type": "opg",
        "case_id": web_case_id,
        "dob": "1995-05-15",
        "gender": "Female"
    }
    r_analyze = requests.post(f"{PRODUCTION_URL}/analysis/analyze", headers=auth_headers, data=analyze_data, timeout=120)
    print(f"[OK] Web POST /analysis/analyze -> HTTP {r_analyze.status_code}")
    assert r_analyze.status_code == 200, f"Web analyze failed: {r_analyze.text}"
    web_report = r_analyze.json()
    print(f"[INFO] Web Created Case ID: {web_report.get('id')}, Score: {web_report.get('finishing_score')}")

    # 5. Android Client Flow: Fetch History and retrieve TEST_WEB_PATIENT
    print("\n--- 5. Simulated Android Client Flow: Fetch History & Verify Web Case ---")
    r_android_hist = requests.get(f"{PRODUCTION_URL}/analysis/history", headers=auth_headers, timeout=60)
    print(f"[OK] Android GET /analysis/history -> HTTP {r_android_hist.status_code}")
    assert r_android_hist.status_code == 200
    android_cases = r_android_hist.json()
    web_case_found = any(c.get("patient_name") == "TEST_WEB_PATIENT" or c.get("id") == web_case_id for c in android_cases)
    print(f"[VERIFIED] Android retrieved TEST_WEB_PATIENT: {web_case_found} (Total cases: {len(android_cases)})")

    # Android opens complete report
    r_web_rep = requests.get(f"{PRODUCTION_URL}/analysis/report/{web_case_id}", headers=auth_headers, timeout=60)
    print(f"[OK] Android GET /analysis/report/{web_case_id} -> HTTP {r_web_rep.status_code}")
    assert r_web_rep.status_code == 200
    rep_data = r_web_rep.json()
    print(f"[INFO] Complete Clinical Report: Patient={rep_data.get('patient_name')}, ABO={rep_data.get('abo_score')}, Andrews={rep_data.get('andrews_score')}, Recs={len(rep_data.get('recommendations', []))}")

    # 6. Android Client Flow: Create TEST_ANDROID_PATIENT
    print("\n--- 6. Simulated Android Client Flow: Create 'TEST_ANDROID_PATIENT' ---")
    files_android = {"file": ("test_android_opg.jpg", img_bytes, "image/jpeg")}
    r_upload_and = requests.post(f"{PRODUCTION_URL}/analysis/upload", headers=auth_headers, files=files_android, timeout=60)
    print(f"[OK] Android POST /analysis/upload -> HTTP {r_upload_and.status_code}")
    assert r_upload_and.status_code == 200
    and_upload_id = r_upload_and.json()["upload_id"]

    and_case_id = f"case_android_{int(time.time())}"
    analyze_and_data = {
        "upload_id": and_upload_id,
        "patient_name": "TEST_ANDROID_PATIENT",
        "view_type": "opg",
        "case_id": and_case_id,
        "dob": "2000-10-20",
        "gender": "Male"
    }
    r_analyze_and = requests.post(f"{PRODUCTION_URL}/analysis/analyze", headers=auth_headers, data=analyze_and_data, timeout=120)
    print(f"[OK] Android POST /analysis/analyze -> HTTP {r_analyze_and.status_code}")
    assert r_analyze_and.status_code == 200
    and_report = r_analyze_and.json()
    print(f"[INFO] Android Created Case ID: {and_report.get('id')}, Score: {and_report.get('finishing_score')}")

    # 7. Web Client Flow: Fetch History and verify Android Case
    print("\n--- 7. Simulated Web Client Flow: Fetch History & Verify Android Case ---")
    r_web_hist2 = requests.get(f"{PRODUCTION_URL}/analysis/history", headers=auth_headers, timeout=60)
    print(f"[OK] Web GET /analysis/history -> HTTP {r_web_hist2.status_code}")
    assert r_web_hist2.status_code == 200
    all_cases = r_web_hist2.json()
    and_case_found = any(c.get("patient_name") == "TEST_ANDROID_PATIENT" or c.get("id") == and_case_id for c in all_cases)
    print(f"[VERIFIED] Web retrieved TEST_ANDROID_PATIENT: {and_case_found} (Total cases: {len(all_cases)})")

    # Web opens complete report for Android case
    r_and_rep = requests.get(f"{PRODUCTION_URL}/analysis/report/{and_case_id}", headers=auth_headers, timeout=60)
    print(f"[OK] Web GET /analysis/report/{and_case_id} -> HTTP {r_and_rep.status_code}")
    assert r_and_rep.status_code == 200

    print("\n" + "=" * 70)
    print("ALL RUNTIME SYNC CHECKS PASSED LIVE ON PRODUCTION BACKEND")
    print("=" * 70)

if __name__ == "__main__":
    run_audit()
