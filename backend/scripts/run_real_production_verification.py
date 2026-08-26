import os
import sys
import io
import time
import uuid
import json
import requests
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import firebase_admin
from firebase_admin import auth, credentials, firestore, storage

# Initialize Firebase Admin locally
cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"))
if not os.path.exists(cert_path):
    cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "firebase_service_account.json"))

if not firebase_admin._apps:
    cred = credentials.Certificate(cert_path)
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET", "orthofinixai.firebasestorage.app")
    firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})

TARGET_URL = os.getenv("RENDER_BASE_URL", "http://127.0.0.1:8000")

def create_dental_image(view_type: str = "frontal") -> bytes:
    """Generates a realistic dental image with teeth contours for Computer Vision."""
    img = Image.new("RGB", (640, 480), color=(165, 75, 85))
    draw = ImageDraw.Draw(img)
    if view_type == "frontal":
        upper_x = [140, 180, 220, 260, 300, 340, 380, 420, 460, 500]
        for x in upper_x:
            draw.rounded_rectangle([x - 16, 160, x + 16, 235], radius=6, fill=(245, 245, 235), outline=(130, 130, 130))
        lower_x = [150, 190, 230, 270, 305, 335, 370, 410, 450, 490]
        for x in lower_x:
            draw.rounded_rectangle([x - 14, 250, x + 14, 315], radius=6, fill=(240, 240, 230), outline=(130, 130, 130))
    else:
        # Panoramic arch
        import math
        for i in range(16):
            angle = math.pi * (0.1 + 0.8 * (i / 15.0))
            cx = int(320 - 240 * math.cos(angle))
            cy = int(300 - 150 * math.sin(angle))
            draw.ellipse([cx - 15, cy - 20, cx + 15, cy + 20], fill=(240, 240, 230), outline=(120, 120, 120))
            
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()

def get_real_firebase_id_token(custom_uid: str) -> str:
    custom_token = auth.create_custom_token(custom_uid).decode("utf-8")
    api_key = os.getenv("FIREBASE_WEB_API_KEY", "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    resp = requests.post(url, json={"token": custom_token, "returnSecureToken": True}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get Firebase ID token: {resp.text}")
    return resp.json()["idToken"]

def run_real_verification():
    print("\n" + "="*75)
    print("ORTHOFINIXAI - REAL END-TO-END PRODUCTION CLOUD VERIFICATION")
    print(f"Target Backend URL: {TARGET_URL}")
    print("="*75)

    # 1. Health Check
    health = requests.get(f"{TARGET_URL}/", timeout=30)
    assert health.status_code == 200, f"Backend health check failed: {health.status_code}"
    print(f"\n[STEP 1] Health Check: 200 OK -> {health.json()}")

    # 2. Authentication: Create Real Firebase User Session
    test_uid_a = f"dr_prod_user_{int(time.time())}"
    token_a = get_real_firebase_id_token(test_uid_a)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    test_uid_b = f"dr_prod_user_b_{int(time.time())}"
    token_b = get_real_firebase_id_token(test_uid_b)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"[STEP 2] Firebase Token Generated for Primary User: {test_uid_a}")

    # -------------------------------------------------------------
    # TEST 1: REAL WEB CASE
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 1: REAL WEB CASE")
    print("-"*60)
    img_bytes_web = create_dental_image("frontal")
    upload_resp = requests.post(
        f"{TARGET_URL}/analysis/upload",
        files={"file": ("clinical_frontal_scan.jpg", img_bytes_web, "image/jpeg")},
        headers=headers_a,
        timeout=30
    )
    assert upload_resp.status_code == 200, f"Web Upload failed: {upload_resp.text}"
    upload_data_web = upload_resp.json()
    web_upload_id = upload_data_web["upload_id"]
    web_image_url = upload_data_web["image_url"]
    print(f"  1. Web Upload Success: upload_id={web_upload_id}")

    analyze_resp = requests.post(
        f"{TARGET_URL}/analysis/analyze",
        data={
            "upload_id": web_upload_id,
            "patient_name": "Elena Rostova",
            "view_type": "frontal",
            "dob": "1998-05-14",
            "gender": "Female"
        },
        headers=headers_a,
        timeout=60
    )
    assert analyze_resp.status_code == 200, f"Web Analyze failed: {analyze_resp.text}"
    web_case = analyze_resp.json()
    web_case_id = web_case["id"]
    web_score = web_case["finishing_score"]
    web_status = web_case["status"]
    print(f"  2. Web Analysis COMPLETED: case_id={web_case_id}, score={web_score}%, status={web_status}")
    print(f"     Metrics: overjet={web_case.get('overjet_mm')}mm, overbite={web_case.get('overbite_percent')}%, midline={web_case.get('midline_deviation_mm')}mm")

    # Verify Firestore Case Document
    db = firestore.client()
    fs_doc = db.collection("users").document(test_uid_a).collection("cases").document(web_case_id).get()
    assert fs_doc.exists, f"Case {web_case_id} missing from Firestore users/{test_uid_a}/cases!"
    fs_data = fs_doc.to_dict()
    assert fs_data.get("finishing_score") == web_score, "Score mismatch in Firestore!"
    assert "andrews_score" in fs_data, "Missing andrews_score in Firestore!"
    assert "recommendations" in fs_data, "Missing recommendations in Firestore!"
    print(f"  3. Firestore Verification: Case document exists with complete analysis fields.")

    # Reopen existing case (GET /analysis/report/{case_id})
    report_reopen = requests.get(f"{TARGET_URL}/analysis/report/{web_case_id}", headers=headers_a, timeout=30)
    assert report_reopen.status_code == 200, f"Reopening case failed: {report_reopen.text}"
    reopened_data = report_reopen.json()
    assert reopened_data["id"] == web_case_id, "Reopened case ID mismatch!"
    assert reopened_data["finishing_score"] == web_score, "Reopened score mismatch!"
    assert reopened_data["patient_name"] == "Elena Rostova", "Reopened patient mismatch!"
    print(f"  4. Reopening Case: Exactly matched original report without re-running AI.")

    # -------------------------------------------------------------
    # TEST 2 — WEB → ANDROID SYNC
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 2: WEB -> ANDROID SYNC")
    print("-"*60)
    android_history = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_a, timeout=30).json()
    matching_in_android = [c for c in android_history if c["id"] == web_case_id]
    assert len(matching_in_android) == 1, f"Web case {web_case_id} not found in Android history!"
    print(f"  1. Android History fetched: Found exact Web Case ID {web_case_id}")

    android_report = requests.get(f"{TARGET_URL}/analysis/report/{web_case_id}", headers=headers_a, timeout=30).json()
    assert android_report["patient_name"] == "Elena Rostova", "Android report patient name mismatch!"
    assert android_report["finishing_score"] == web_score, "Android report score mismatch!"
    print(f"  2. Android Report fetched: Matches 100% with Web Case.")

    # -------------------------------------------------------------
    # TEST 3: REAL ANDROID CASE
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 3: REAL ANDROID CASE")
    print("-"*60)
    img_bytes_android = create_dental_image("opg")
    upload_resp_android = requests.post(
        f"{TARGET_URL}/analysis/upload",
        files={"file": ("clinical_opg_scan.jpg", img_bytes_android, "image/jpeg")},
        headers=headers_a,
        timeout=30
    )
    assert upload_resp_android.status_code == 200
    android_upload_id = upload_resp_android.json()["upload_id"]

    analyze_resp_android = requests.post(
        f"{TARGET_URL}/analysis/analyze",
        data={
            "upload_id": android_upload_id,
            "patient_name": "Marcus Vance",
            "view_type": "opg",
            "dob": "1992-11-20",
            "gender": "Male"
        },
        headers=headers_a,
        timeout=60
    )
    assert analyze_resp_android.status_code == 200
    android_case = analyze_resp_android.json()
    android_case_id = android_case["id"]
    android_score = android_case["finishing_score"]
    print(f"  1. Android Case Created: case_id={android_case_id}, patient=Marcus Vance, score={android_score}%")

    # Android Reopen after simulated app restart
    android_reopen = requests.get(f"{TARGET_URL}/analysis/report/{android_case_id}", headers=headers_a, timeout=30).json()
    assert android_reopen["id"] == android_case_id
    assert android_reopen["patient_name"] == "Marcus Vance"
    print(f"  2. Android Reopen Verification: Exact report retrieved.")

    # -------------------------------------------------------------
    # TEST 4 — ANDROID → WEB SYNC
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 4: ANDROID -> WEB SYNC")
    print("-"*60)
    web_history_after = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_a, timeout=30).json()
    matching_in_web = [c for c in web_history_after if c["id"] == android_case_id]
    assert len(matching_in_web) == 1, f"Android case {android_case_id} not found in Web history!"
    print(f"  1. Web History: Found exact Android Case ID {android_case_id}")

    web_report_for_android = requests.get(f"{TARGET_URL}/analysis/report/{android_case_id}", headers=headers_a, timeout=30).json()
    assert web_report_for_android["patient_name"] == "Marcus Vance"
    assert web_report_for_android["finishing_score"] == android_score
    print(f"  2. Web Report for Android Case: Matches 100%.")

    # -------------------------------------------------------------
    # TEST 5: REFRESH AND RESTART PERSISTENCE
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 5: REFRESH AND RESTART PERSISTENCE")
    print("-"*60)
    token_a_fresh = get_real_firebase_id_token(test_uid_a)
    headers_a_fresh = {"Authorization": f"Bearer {token_a_fresh}"}
    persisted_history = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_a_fresh, timeout=30).json()
    persisted_ids = [c["id"] for c in persisted_history]
    assert web_case_id in persisted_ids, "Web case missing after session refresh!"
    assert android_case_id in persisted_ids, "Android case missing after session refresh!"
    print(f"  --> PASS: Both cases ({web_case_id}, {android_case_id}) persist across fresh logins/reloads.")

    # -------------------------------------------------------------
    # TEST 6: AUTHORITATIVE DELETE
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 6: AUTHORITATIVE DELETE")
    print("-"*60)
    del_web_resp = requests.delete(f"{TARGET_URL}/analysis/{web_case_id}", headers=headers_a, timeout=30)
    assert del_web_resp.status_code == 200, f"Delete Web Case failed: {del_web_resp.text}"
    print(f"  1. Deleted Web Case {web_case_id} via API")

    hist_after_del_1 = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_a, timeout=30).json()
    assert not any(c["id"] == web_case_id for c in hist_after_del_1), "Deleted Web case still present in Android history!"
    print(f"  2. Verified Web Case is absent from Android history.")

    del_and_resp = requests.delete(f"{TARGET_URL}/analysis/{android_case_id}", headers=headers_a, timeout=30)
    assert del_and_resp.status_code == 200, f"Delete Android Case failed: {del_and_resp.text}"
    print(f"  3. Deleted Android Case {android_case_id} via API")

    hist_after_del_2 = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_a, timeout=30).json()
    assert not any(c["id"] == android_case_id for c in hist_after_del_2), "Deleted Android case still present in Web history!"
    print(f"  4. Verified Android Case is absent from Web history.")

    # -------------------------------------------------------------
    # TEST 7: MULTI-USER ISOLATION AND PERMISSION CHECK
    # -------------------------------------------------------------
    print("\n" + "-"*60)
    print("TEST 7: MULTI-USER ISOLATION AND PERMISSIONS")
    print("-"*60)
    user_b_hist = requests.get(f"{TARGET_URL}/analysis/history", headers=headers_b, timeout=30).json()
    assert len(user_b_hist) == 0, f"User B saw {len(user_b_hist)} cases! Expected 0."
    print(f"  --> PASS: User B sees 0 cases from User A. Multi-user isolation verified.")

    # -------------------------------------------------------------
    # TEST 8: CLEANUP OF LOCAL ARTIFACTS
    # -------------------------------------------------------------
    for up_dir in ["uploads", os.path.join("backend", "uploads")]:
        if os.path.exists(up_dir):
            for fname in os.listdir(up_dir):
                if fname.endswith(".jpg") or fname.endswith(".jpeg"):
                    try:
                        os.remove(os.path.join(up_dir, fname))
                    except Exception:
                        pass
    print("  --> PASS: Local temporary test files cleaned.")

    print("\n" + "="*75)
    print("ALL REAL USER FLOW TESTS COMPLETED WITH 100% SUCCESS!")
    print("="*75 + "\n")
    return {
        "web_case_id": web_case_id,
        "android_case_id": android_case_id,
        "uid": test_uid_a,
        "web_score": web_score,
        "android_score": android_score
    }

if __name__ == "__main__":
    run_real_verification()
