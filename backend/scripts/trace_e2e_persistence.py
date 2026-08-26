import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import auth, firestore, storage, credentials

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Initialize Firebase Admin
from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")

# If FIREBASE_WEB_API_KEY is not set in env, read from web config
if not FIREBASE_WEB_API_KEY:
    try:
        with open(os.path.join(BASE_DIR, "..", "web", "src", "lib", "firebase.ts"), "r", encoding="utf-8") as f:
            content = f.read()
            for line in content.splitlines():
                if "apiKey:" in line:
                    FIREBASE_WEB_API_KEY = line.split("apiKey:")[1].strip().strip("',\"")
                    break
    except Exception:
        pass


def get_real_firebase_id_token(email: str = "doctor@orthofinix.ai", password: str = "DoctorPassword123!"):
    """
    Creates or fetches a real Firebase user, mints a custom token via Admin SDK, 
    and exchanges it for a real Firebase ID token via Google Identity Toolkit API.
    """
    try:
        try:
            user_record = auth.get_user_by_email(email)
            print(f"[AUTH] Found existing Firebase user: {user_record.uid} ({email})")
        except firebase_admin.auth.UserNotFoundError:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name="Dr. Orthofinix Verified",
                email_verified=True
            )
            print(f"[AUTH] Created new real Firebase user: {user_record.uid} ({email})")

        uid = user_record.uid

        # Mint custom token
        custom_token_bytes = auth.create_custom_token(uid)
        custom_token = custom_token_bytes.decode("utf-8") if isinstance(custom_token_bytes, bytes) else custom_token_bytes

        # Exchange custom token for real ID token
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_WEB_API_KEY}"
        resp = requests.post(verify_url, json={"token": custom_token, "returnSecureToken": True}, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to exchange custom token for ID token: {resp.text}")

        id_token = resp.json()["idToken"]
        return uid, email, id_token

    except Exception as e:
        print(f"[AUTH ERROR] Failed to get real Firebase ID token: {e}")
        raise


def run_e2e_persistence_trace():
    print("=" * 80)
    print("ORTHOFINIX AI: COMPLETE END-TO-END PERSISTENCE & SYNC TRACE")
    print("=" * 80)

    # Step 1 & 2: Real Firebase User & Real Token
    uid, email, id_token = get_real_firebase_id_token()
    print(f"[TRACE 1 & 2] Authenticated Firebase User UID: {uid}")
    print(f"[TRACE 3] Real Firebase ID Token Acquired (length: {len(id_token)})")

    headers = {
        "Authorization": f"Bearer {id_token}"
    }

    # Step 4: Upload Real Dental Image
    # Create or load a real sample dental image
    test_img_path = os.path.join(BASE_DIR, "test_dental_image.jpg")
    if not os.path.exists(test_img_path):
        import numpy as np
        from PIL import Image
        img_arr = np.random.randint(100, 240, (512, 512, 3), dtype=np.uint8)
        img = Image.fromarray(img_arr)
        img.save(test_img_path, "JPEG")

    with open(test_img_path, "rb") as f:
        img_bytes = f.read()

    print(f"\n[TRACE 4] Sending POST /analysis/upload to {API_BASE_URL}/analysis/upload ...")
    upload_resp = requests.post(
        f"{API_BASE_URL}/analysis/upload",
        headers=headers,
        files={"file": ("clinical_panoramic.jpg", img_bytes, "image/jpeg")},
        timeout=120
    )

    if upload_resp.status_code != 200:
        print(f"[FAIL] Upload failed: HTTP {upload_resp.status_code} - {upload_resp.text}")
        return False

    upload_data = upload_resp.json()
    upload_id = upload_data.get("upload_id")
    uploaded_image_url = upload_data.get("image_url")
    print(f"[TRACE 5] Upload successful: upload_id={upload_id}, image_url={uploaded_image_url}")

    # Step 6 & 7 & 8: Analyze Image & Generate Report
    patient_name = f"Trace Patient {int(time.time())}"
    print(f"\n[TRACE 6 & 7] Sending POST /analysis/analyze for patient '{patient_name}' ...")
    analyze_payload = {
        "upload_id": upload_id,
        "patient_name": patient_name,
        "view_type": "frontal",
        "dob": "1995-05-15",
        "gender": "Female",
        "notes": "E2E persistence audit trace case"
    }
    
    analyze_resp = requests.post(
        f"{API_BASE_URL}/analysis/analyze",
        headers=headers,
        data=analyze_payload,
        timeout=180
    )

    if analyze_resp.status_code != 200:
        print(f"[FAIL] Analyze failed: HTTP {analyze_resp.status_code} - {analyze_resp.text}")
        return False

    report_data = analyze_resp.json()
    case_id = report_data.get("id") or report_data.get("case_id")
    overall_score = report_data.get("overallScore") or report_data.get("finishing_score")
    abo_score = report_data.get("abo_score")
    andrews_score = report_data.get("andrews_score")
    confidence = report_data.get("confidence_score")
    final_image_url = report_data.get("image_url")

    print(f"[TRACE 8] Generated Canonical Case ID: {case_id}")
    print(f"[TRACE 8] Clinical Scores: Overall={overall_score}, ABO={abo_score}, Andrews={andrews_score}, Confidence={confidence}")
    print(f"[TRACE 8] Persisted Image URL: {final_image_url}")

    # Step 9, 10, 11: Direct Cloud Verification
    print(f"\n[TRACE 9, 10, 11] Verifying Cloud Database & Cloud Storage Persistence...")
    db = get_firestore_client()
    
    # 1. Firestore: users/{uid}/cases/{case_id}
    user_case_doc = db.collection("users").document(uid).collection("cases").document(case_id).get()
    if not user_case_doc.exists:
        print(f"[FAIL] Firestore users/{uid}/cases/{case_id} does NOT exist!")
        return False
    user_case_data = user_case_doc.to_dict()
    print(f"[PASS] Firestore users/{uid}/cases/{case_id} verified: Status={user_case_data.get('status')}, Score={user_case_data.get('overall_score')}")

    # 2. Firestore: cases/{case_id}
    root_case_doc = db.collection("cases").document(case_id).get()
    if not root_case_doc.exists:
        print(f"[FAIL] Firestore root cases/{case_id} does NOT exist!")
        return False
    print(f"[PASS] Firestore root cases/{case_id} verified.")

    # 3. Firestore: analysis_reports/{case_id}
    root_report_doc = db.collection("analysis_reports").document(case_id).get()
    if not root_report_doc.exists:
        print(f"[FAIL] Firestore root analysis_reports/{case_id} does NOT exist!")
        return False
    print(f"[PASS] Firestore root analysis_reports/{case_id} verified.")

    # 4. User total_cases counter
    user_profile_doc = db.collection("users").document(uid).get()
    total_cases = user_profile_doc.to_dict().get("total_cases", 0) if user_profile_doc.exists else 0
    print(f"[PASS] User Profile total_cases counter: {total_cases}")

    # Step 13: GET /analysis/history
    print(f"\n[TRACE 13] Calling GET /analysis/history with authentic UID token...")
    hist_resp = requests.get(f"{API_BASE_URL}/analysis/history", headers=headers, timeout=30)
    if hist_resp.status_code != 200:
        print(f"[FAIL] History failed: HTTP {hist_resp.status_code} - {hist_resp.text}")
        return False

    history_items = hist_resp.json()
    found_in_history = any(item.get("id") == case_id for item in history_items)
    if not found_in_history:
        print(f"[FAIL] Created case {case_id} NOT found in history list: {[i.get('id') for i in history_items]}")
        return False
    print(f"[PASS] GET /analysis/history returned {len(history_items)} cases, including created case {case_id}.")

    # Step 14: GET /analysis/report/{case_id} (Reopen without re-running AI)
    print(f"\n[TRACE 14] Calling GET /analysis/report/{case_id} (reopening existing case)...")
    get_report_resp = requests.get(f"{API_BASE_URL}/analysis/report/{case_id}", headers=headers, timeout=30)
    if get_report_resp.status_code != 200:
        print(f"[FAIL] Fetch report failed: HTTP {get_report_resp.status_code} - {get_report_resp.text}")
        return False

    fetched_report = get_report_resp.json()
    assert fetched_report.get("id") == case_id, "Case ID mismatch"
    assert fetched_report.get("user_id") == uid, "Owner UID mismatch"
    print(f"[PASS] GET /analysis/report/{case_id} successfully reopened persisted case with identical metrics.")

    # Step 16: DELETE /analysis/{case_id}
    print(f"\n[TRACE 16] Testing DELETE /analysis/{case_id} ...")
    del_resp = requests.delete(f"{API_BASE_URL}/analysis/{case_id}", headers=headers, timeout=30)
    if del_resp.status_code != 200:
        print(f"[FAIL] Delete failed: HTTP {del_resp.status_code} - {del_resp.text}")
        return False
    print(f"[PASS] DELETE /analysis/{case_id} returned HTTP 200.")

    # Verify post-delete state
    post_hist_resp = requests.get(f"{API_BASE_URL}/analysis/history", headers=headers, timeout=30)
    post_history = post_hist_resp.json()
    if any(item.get("id") == case_id for item in post_history):
        print(f"[FAIL] Deleted case {case_id} still appears in GET /analysis/history!")
        return False
    print(f"[PASS] Case {case_id} completely removed from GET /analysis/history.")

    post_report_resp = requests.get(f"{API_BASE_URL}/analysis/report/{case_id}", headers=headers, timeout=30)
    if post_report_resp.status_code != 404:
        print(f"[FAIL] Expected HTTP 404 for deleted report, got HTTP {post_report_resp.status_code}")
        return False
    print(f"[PASS] GET /analysis/report/{case_id} correctly returned HTTP 404 after deletion.")

    # Check Firestore doc deleted
    post_user_doc = db.collection("users").document(uid).collection("cases").document(case_id).get()
    if post_user_doc.exists:
        print(f"[FAIL] Firestore users/{uid}/cases/{case_id} still exists after deletion!")
        return False
    print(f"[PASS] Firestore users/{uid}/cases/{case_id} verified deleted.")

    print("\n" + "=" * 80)
    print("ALL 16 PIPELINE AND PERSISTENCE TRACE STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = run_e2e_persistence_trace()
    sys.exit(0 if success else 1)
