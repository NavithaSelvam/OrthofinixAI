import os
import sys
import io
import json
import uuid
import requests
from PIL import Image, ImageDraw
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

FIREBASE_WEB_API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"

def get_id_token_for_uid(uid: str, email: str = "test@orthofinix.ai") -> str:
    """
    Mints a custom token using Firebase Admin SDK and exchanges it for a real Firebase ID token.
    """
    try:
        # Create or verify user exists in Firebase Auth
        try:
            auth.get_user(uid)
        except auth.UserNotFoundError:
            auth.create_user(uid=uid, email=email)
        
        custom_token = auth.create_custom_token(uid)
        if isinstance(custom_token, bytes):
            custom_token = custom_token.decode("utf-8")
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_WEB_API_KEY}"
        res = requests.post(url, json={"token": custom_token, "returnSecureToken": True})
        res.raise_for_status()
        return res.json()["idToken"]
    except Exception as e:
        print(f"Failed to get Firebase ID token for UID {uid}: {e}")
        raise

def create_sample_intraoral_image() -> bytes:
    img = Image.new("RGB", (600, 450), color=(170, 45, 60))
    draw = ImageDraw.Draw(img)
    # Upper arch smile teeth
    for x in range(120, 480, 45):
        draw.ellipse([x, 150, x + 38, 230], fill=(245, 245, 238), outline=(200, 200, 190))
    # Lower arch teeth
    for x in range(135, 465, 42):
        draw.ellipse([x, 240, x + 34, 305], fill=(245, 245, 238), outline=(200, 200, 190))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

def run_real_uid_cross_platform_audit():
    print("=" * 80)
    print("ORTHOFINIX AI: REAL FIREBASE UID OWNERSHIP & CROSS-PLATFORM AUDIT")
    print("=" * 80)

    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # 1. USER A (Primary Real Doctor Account)
    user_a_uid = "ArYEcygXQ8W9ZecRUQbfpqTDQK92"
    user_a_email = "navithselvam07@gmail.com"
    print(f"\n[STEP 1] Authenticating USER A: {user_a_email} (UID: {user_a_uid})")
    user_a_token = get_id_token_for_uid(user_a_uid, user_a_email)
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    print(f" -> ID Token successfully obtained from Firebase Auth.")

    # 2. Verify GET /auth/me for USER A
    print("\n[STEP 2] Calling GET /auth/me with USER A Bearer token...")
    me_res_a = client.get("/auth/me", headers=headers_a)
    assert me_res_a.status_code == 200, f"GET /auth/me failed: {me_res_a.text}"
    me_data_a = me_res_a.json()
    print(f" -> GET /auth/me Response: {me_data_a}")
    assert me_data_a["uid"] == user_a_uid, f"Expected UID {user_a_uid}, got {me_data_a['uid']}"
    assert me_data_a["email"] == user_a_email, f"Expected Email {user_a_email}, got {me_data_a['email']}"
    print(" -> [PASS] Verified authentic Firebase UID matches token.")

    # 3. Create Case A for USER A
    print("\n[STEP 3] Creating Real Clinical Case A for USER A...")
    img_bytes = create_sample_intraoral_image()
    upload_res = client.post(
        "/analysis/upload",
        headers=headers_a,
        files={"file": ("clinical_case_a.jpg", img_bytes, "image/jpeg")}
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_id = upload_res.json()["upload_id"]
    print(f" -> Upload succeeded: upload_id={upload_id}")

    test_case_id = f"CASE_AUDIT_{uuid.uuid4().hex[:8]}"
    analyze_res = client.post(
        "/analysis/analyze",
        headers=headers_a,
        data={
            "upload_id": upload_id,
            "patient_name": "Suji Real Patient",
            "view_type": "frontal",
            "case_id": test_case_id,
            "dob": "1998-05-12",
            "gender": "Female"
        }
    )
    assert analyze_res.status_code == 200, f"Analysis failed: {analyze_res.text}"
    report_data = analyze_res.json()
    created_case_id = report_data["case_id"] or report_data["id"]
    print(f" -> Analysis succeeded: case_id={created_case_id}, score={report_data['overallScore']}%")

    # 4. Verify Firestore ownership
    print("\n[STEP 4] Verifying Firestore Document Ownership for Case A...")
    
    # 4a. Check users/{user_a_uid}/cases/{created_case_id}
    sub_doc = db.collection("users").document(user_a_uid).collection("cases").document(created_case_id).get()
    assert sub_doc.exists, f"Subcollection doc users/{user_a_uid}/cases/{created_case_id} does not exist!"
    sub_data = sub_doc.to_dict()
    print(f" -> users/{user_a_uid}/cases/{created_case_id} user_id={sub_data.get('user_id')}, doctor_id={sub_data.get('doctor_id')}")
    assert sub_data.get("user_id") == user_a_uid, f"Expected user_id {user_a_uid}, got {sub_data.get('user_id')}"
    assert sub_data.get("doctor_id") == user_a_uid, f"Expected doctor_id {user_a_uid}, got {sub_data.get('doctor_id')}"

    # 4b. Check root cases/{created_case_id}
    root_case_doc = db.collection("cases").document(created_case_id).get()
    assert root_case_doc.exists, f"Root cases/{created_case_id} does not exist!"
    root_case_data = root_case_doc.to_dict()
    print(f" -> cases/{created_case_id} user_id={root_case_data.get('user_id')}, doctor_id={root_case_data.get('doctor_id')}")
    assert root_case_data.get("user_id") == user_a_uid
    assert root_case_data.get("doctor_id") == user_a_uid

    # 4c. Check root analysis_reports/{created_case_id}
    report_doc = db.collection("analysis_reports").document(created_case_id).get()
    assert report_doc.exists, f"analysis_reports/{created_case_id} does not exist!"
    report_fs_data = report_doc.to_dict()
    print(f" -> analysis_reports/{created_case_id} user_id={report_fs_data.get('user_id')}")
    assert report_fs_data.get("user_id") == user_a_uid

    # 4d. Check patient doctor_id
    pat_id = report_data.get("patient_id") or sub_data.get("patient_id")
    if pat_id:
        pat_doc = db.collection("patients").document(pat_id).get()
        if pat_doc.exists:
            p_data = pat_doc.to_dict()
            print(f" -> patients/{pat_id} doctor_id={p_data.get('doctor_id')}")
            assert p_data.get("doctor_id") == user_a_uid, f"Expected patient doctor_id {user_a_uid}, got {p_data.get('doctor_id')}"

    print(" -> [PASS] All Firestore documents verified with REAL Firebase UID.")

    # 5. Verify GET /analysis/history for USER A
    print("\n[STEP 5] Calling GET /analysis/history for USER A...")
    hist_res_a = client.get("/analysis/history", headers=headers_a)
    assert hist_res_a.status_code == 200, f"History fetch failed: {hist_res_a.text}"
    history_a = hist_res_a.json()
    matching_a = [item for item in history_a if item["id"] == created_case_id or item.get("case_id") == created_case_id]
    assert len(matching_a) == 1, f"Case {created_case_id} not found in USER A history!"
    print(f" -> [PASS] Case A successfully found in USER A history (Total: {len(history_a)} cases).")

    # 6. Authenticate USER B and verify strict cross-user isolation
    user_b_uid = f"doctor_user_b_{uuid.uuid4().hex[:8]}"
    user_b_email = f"user_b_{uuid.uuid4().hex[:6]}@orthofinix.ai"
    print(f"\n[STEP 6] Authenticating USER B: {user_b_email} (UID: {user_b_uid})...")
    user_b_token = get_id_token_for_uid(user_b_uid, user_b_email)
    headers_b = {"Authorization": f"Bearer {user_b_token}"}

    me_res_b = client.get("/auth/me", headers=headers_b)
    assert me_res_b.status_code == 200
    assert me_res_b.json()["uid"] == user_b_uid

    print(" -> Calling GET /analysis/history for USER B...")
    hist_res_b = client.get("/analysis/history", headers=headers_b)
    assert hist_res_b.status_code == 200
    history_b = hist_res_b.json()
    matching_b = [item for item in history_b if item["id"] == created_case_id or item.get("case_id") == created_case_id]
    assert len(matching_b) == 0, f"SECURITY VIOLATION: USER B can see USER A's case {created_case_id}!"
    print(" -> [PASS] Strict User Isolation verified: USER B cannot see USER A's case.")

    # 7. Re-authenticate USER A & Delete Case A
    print("\n[STEP 7] Re-authenticating USER A and executing DELETE /analysis/{created_case_id}...")
    del_res = client.delete(f"/analysis/{created_case_id}", headers=headers_a)
    assert del_res.status_code == 200, f"Delete failed: {del_res.text}"
    print(f" -> Delete response: {del_res.json()}")

    # Verify document is deleted from Firestore
    sub_after = db.collection("users").document(user_a_uid).collection("cases").document(created_case_id).get()
    assert not sub_after.exists, f"Document still exists in users/{user_a_uid}/cases/{created_case_id}!"
    root_case_after = db.collection("cases").document(created_case_id).get()
    assert not root_case_after.exists, f"Document still exists in root cases/{created_case_id}!"
    print(" -> [PASS] Verified case deleted from subcollection and root collection.")

    # 8. Verify case no longer in USER A history
    hist_after_a = client.get("/analysis/history", headers=headers_a).json()
    matching_after = [item for item in hist_after_a if item["id"] == created_case_id or item.get("case_id") == created_case_id]
    assert len(matching_after) == 0, f"Case {created_case_id} still returned in history after deletion!"
    print(" -> [PASS] Verified case permanently removed from history.")

    # Clean up test user B
    try:
        auth.delete_user(user_b_uid)
        db.collection("users").document(user_b_uid).delete()
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("ALL REAL FIREBASE UID OWNERSHIP CHECKS PASSED WITH ZERO ERRORS!")
    print("=" * 80)

if __name__ == "__main__":
    run_real_uid_cross_platform_audit()
