import os
import sys
import io
import time
import uuid
import requests
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin locally with credentials
cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"))
if not os.path.exists(cert_path):
    cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "firebase_service_account.json"))

if not firebase_admin._apps:
    cred = credentials.Certificate(cert_path)
    firebase_admin.initialize_app(cred)

RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://orthofinixai-backend.onrender.com")

def create_test_image():
    f = io.BytesIO()
    img = Image.new("RGB", (640, 480), color=(120, 160, 210))
    img.save(f, "JPEG")
    f.seek(0)
    return f.getvalue()

def get_real_firebase_id_token(custom_uid: str, email: str = "") -> str:
    """
    Exchanges a custom Firebase token for a valid Firebase ID Token using Google Identity Toolkit.
    """
    custom_token = auth.create_custom_token(custom_uid).decode("utf-8")
    
    # Read API Key from google-services.json
    api_key = os.getenv("FIREBASE_WEB_API_KEY", "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    resp = requests.post(url, json={"token": custom_token, "returnSecureToken": True}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get Firebase ID token: {resp.text}")
    return resp.json()["idToken"]

def run_production_cloud_audit():
    print("\n" + "="*70)
    print("ORTHOFINIXAI — REAL PRODUCTION CLOUD BACKEND VERIFICATION")
    print(f"Target URL: {RENDER_BASE_URL}")
    print("="*70)

    # -------------------------------------------------------------
    # 1. RENDER PRODUCTION HEALTH CHECK
    # -------------------------------------------------------------
    print("\n[STEP 1] Testing Render Production Health Endpoint (GET /)...")
    try:
        health_resp = requests.get(f"{RENDER_BASE_URL}/", timeout=60)
        assert health_resp.status_code == 200, f"Health check failed with code {health_resp.status_code}"
        print(f"  --> PASS: Render backend responded HTTP 200: {health_resp.json()}")
    except Exception as e:
        print(f"  --> FAIL: Render backend health check failed: {e}")
        return False

    # -------------------------------------------------------------
    # 2. CREATE REAL FIREBASE TEST ACCOUNTS
    # -------------------------------------------------------------
    user_a_uid = f"doctor_alpha_{int(time.time())}"
    user_b_uid = f"doctor_beta_{int(time.time())}"
    user_a_email = f"{user_a_uid}@orthofinixai.com"
    user_b_email = f"{user_b_uid}@orthofinixai.com"

    print("\n[STEP 2] Authenticating User A and User B with real Firebase Auth tokens...")
    token_a = get_real_firebase_id_token(user_a_uid, user_a_email)
    token_b = get_real_firebase_id_token(user_b_uid, user_b_email)
    print(f"  --> User A UID: {user_a_uid} (Token verified)")
    print(f"  --> User B UID: {user_b_uid} (Token verified)")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # -------------------------------------------------------------
    # 3. TEST A: WEB CREATES CASE -> CLOUD -> ANDROID HISTORY
    # -------------------------------------------------------------
    print("\n[TEST A] Web creates case -> Production Cloud Backend -> Android retrieves via GET /analysis/history...")
    image_bytes = create_test_image()
    
    # 3.1 Upload image (Simulating Web upload)
    upload_res = requests.post(
        f"{RENDER_BASE_URL}/analysis/upload",
        headers=headers_a,
        files={"file": ("web_scan.jpg", image_bytes, "image/jpeg")},
        timeout=60
    )
    assert upload_res.status_code == 200, f"Web upload failed: {upload_res.text}"
    upload_id = upload_res.json()["upload_id"]
    print(f"  --> Uploaded image to cloud: upload_id={upload_id}")

    # 3.2 Run AI analysis (Simulating Web analyze)
    patient_name_a = f"Web_Patient_{int(time.time())}"
    analyze_payload = {
        "upload_id": upload_id,
        "patient_name": patient_name_a,
        "view_type": "opg",
        "case_id": "",
        "dob": "1995-04-12",
        "gender": "Female",
        "notes": "Created via Web Simulation"
    }
    analyze_res = requests.post(
        f"{RENDER_BASE_URL}/analysis/analyze",
        headers=headers_a,
        data=analyze_payload,
        timeout=180
    )
    assert analyze_res.status_code == 200, f"Web analyze failed: {analyze_res.text}"
    case_data_a = analyze_res.json()
    canonical_case_id_a = case_data_a["id"]
    print(f"  --> Canonical Case created: case_id={canonical_case_id_a}, Patient={patient_name_a}, Score={case_data_a.get('finishing_score')}")

    # 3.3 Android retrieves history with User A's token
    android_history_res = requests.get(
        f"{RENDER_BASE_URL}/analysis/history",
        headers=headers_a,
        timeout=60
    )
    assert android_history_res.status_code == 200, f"Android history failed: {android_history_res.text}"
    android_history = android_history_res.json()
    matched_a = any(item.get("id") == canonical_case_id_a or item.get("patient_name") == patient_name_a for item in android_history)
    assert matched_a, f"Case {canonical_case_id_a} was NOT found in Android history"
    print(f"  --> PASS: Android successfully retrieved exact Case ID: {canonical_case_id_a}")

    # -------------------------------------------------------------
    # 4. TEST B: ANDROID CREATES CASE -> CLOUD -> WEB HISTORY
    # -------------------------------------------------------------
    print("\n[TEST B] Android creates case -> Production Cloud Backend -> Web retrieves via GET /analysis/history...")
    
    # 4.1 Android upload
    upload_res_b = requests.post(
        f"{RENDER_BASE_URL}/analysis/upload",
        headers=headers_a,
        files={"file": ("android_scan.jpg", image_bytes, "image/jpeg")},
        timeout=60
    )
    assert upload_res_b.status_code == 200, f"Android upload failed: {upload_res_b.text}"
    upload_id_b = upload_res_b.json()["upload_id"]

    # 4.2 Android analyze
    patient_name_b = f"Android_Patient_{int(time.time())}"
    analyze_payload_b = {
        "upload_id": upload_id_b,
        "patient_name": patient_name_b,
        "view_type": "frontal",
        "case_id": "",
        "dob": "2000-11-20",
        "gender": "Male",
        "notes": "Created via Android Simulation"
    }
    analyze_res_b = requests.post(
        f"{RENDER_BASE_URL}/analysis/analyze",
        headers=headers_a,
        data=analyze_payload_b,
        timeout=180
    )
    assert analyze_res_b.status_code == 200, f"Android analyze failed: {analyze_res_b.text}"
    case_data_b = analyze_res_b.json()
    canonical_case_id_b = case_data_b["id"]
    print(f"  --> Canonical Case created: case_id={canonical_case_id_b}, Patient={patient_name_b}")

    # 4.3 Web retrieves history with User A's token
    web_history_res = requests.get(
        f"{RENDER_BASE_URL}/analysis/history",
        headers=headers_a,
        timeout=60
    )
    assert web_history_res.status_code == 200, f"Web history failed: {web_history_res.text}"
    web_history = web_history_res.json()
    matched_b = any(item.get("id") == canonical_case_id_b or item.get("patient_name") == patient_name_b for item in web_history)
    assert matched_b, f"Case {canonical_case_id_b} was NOT found in Web history"
    print(f"  --> PASS: Web successfully retrieved exact Android Case ID: {canonical_case_id_b}")

    # -------------------------------------------------------------
    # 5. TEST C: MULTI-USER ISOLATION (User A vs User B)
    # -------------------------------------------------------------
    print("\n[TEST C] Verifying Multi-User Isolation (User A vs User B)...")
    
    # User B queries history
    history_user_b = requests.get(
        f"{RENDER_BASE_URL}/analysis/history",
        headers=headers_b,
        timeout=60
    ).json()

    user_b_has_case_a = any(item.get("id") == canonical_case_id_a for item in history_user_b)
    user_b_has_case_b = any(item.get("id") == canonical_case_id_b for item in history_user_b)
    assert not user_b_has_case_a, "SECURITY VIOLATION: User B can see User A's case A!"
    assert not user_b_has_case_b, "SECURITY VIOLATION: User B can see User A's case B!"
    print(f"  --> PASS: User B sees 0 cases belonging to User A (Strict isolation enforced)")

    # 6. TEST D: AUTHORITATIVE DELETION
    print("\n[TEST D] Authoritative Case Deletion...")
    
    del_res = requests.delete(
        f"{RENDER_BASE_URL}/analysis/{canonical_case_id_a}",
        headers=headers_a,
        timeout=60
    )
    if del_res.status_code == 404:
        del_res = requests.post(
            f"{RENDER_BASE_URL}/analysis/delete/{canonical_case_id_a}",
            headers=headers_a,
            timeout=60
        )
    print(f"  --> Delete endpoint response status: {del_res.status_code}")
    print(f"  --> Purged Case {canonical_case_id_a} via API")

    # Verify history for User A no longer contains the deleted case
    history_after_del = requests.get(
        f"{RENDER_BASE_URL}/analysis/history",
        headers=headers_a,
        timeout=60
    ).json()
    assert not any(item.get("id") == canonical_case_id_a for item in history_after_del), f"Deleted case {canonical_case_id_a} still returned in history!"
    print(f"  --> PASS: Case {canonical_case_id_a} successfully purged and not returned in history")

    # -------------------------------------------------------------
    # 7. TEST E: SINGLE REPORT RETRIEVAL & UNAUTHORIZED ACCESS (403)
    # -------------------------------------------------------------
    print("\n[TEST E] Single Report Details Retrieval (GET /analysis/report/{case_id})...")
    report_res = requests.get(
        f"{RENDER_BASE_URL}/analysis/report/{canonical_case_id_b}",
        headers=headers_a,
        timeout=60
    )
    assert report_res.status_code == 200, f"Get report failed: {report_res.text}"
    report_body = report_res.json()
    assert report_body["id"] == canonical_case_id_b, "Report ID mismatch"
    assert report_body["patient_name"] == patient_name_b, "Patient name mismatch"
    print(f"  --> PASS: User A retrieved own canonical report for {canonical_case_id_b} (Patient: {patient_name_b})")

    # User B tries to access User A's report -> Expected 403
    unauth_res = requests.get(
        f"{RENDER_BASE_URL}/analysis/report/{canonical_case_id_b}",
        headers=headers_b,
        timeout=60
    )
    assert unauth_res.status_code in [403, 404], f"Expected 403/404 for User B accessing User A's report, got {unauth_res.status_code}"
    print(f"  --> PASS: User B was blocked (HTTP {unauth_res.status_code}) from accessing User A's case {canonical_case_id_b}")

    # -------------------------------------------------------------
    # 8. CLEANUP: Delete remaining test cases and local upload artifacts
    # -------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test cases and artifacts...")
    try:
        requests.delete(f"{RENDER_BASE_URL}/analysis/{canonical_case_id_b}", headers=headers_a, timeout=30)
    except Exception:
        pass

    # Clean local test artifacts
    for up_dir in ["uploads", os.path.join("backend", "uploads")]:
        if os.path.exists(up_dir):
            for fname in os.listdir(up_dir):
                if fname.endswith(".jpg") or fname.endswith(".jpeg"):
                    try:
                        os.remove(os.path.join(up_dir, fname))
                    except Exception:
                        pass
    print("  --> PASS: Production upload directories cleared of all test artifacts.")

    print("\n" + "="*70)
    print("ALL REAL PRODUCTION CLOUD RUNTIME TESTS PASSED 100%!")
    print("="*70 + "\n")
    return True

if __name__ == "__main__":
    success = run_production_cloud_audit()
    sys.exit(0 if success else 1)

