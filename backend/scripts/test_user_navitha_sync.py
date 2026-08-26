import os
import sys
import json
import time
import requests
import firebase_admin
from firebase_admin import auth, firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Load Web API key
FIREBASE_WEB_API_KEY = ""
try:
    with open(os.path.join(BASE_DIR, "..", "web", "src", "lib", "firebase.ts"), "r", encoding="utf-8") as f:
        for line in f:
            if "apiKey:" in line:
                FIREBASE_WEB_API_KEY = line.split("apiKey:")[1].strip().strip("',\"")
                break
except Exception:
    pass


def run_navitha_trace():
    user_email = "navithaselvam07@gmail.com"
    user_record = auth.get_user_by_email(user_email)
    uid = user_record.uid
    print(f"[1. AUTHENTIC USER] Email: {user_email}, UID: {uid}")

    # Mint custom token & exchange for ID token
    custom_token_bytes = auth.create_custom_token(uid)
    custom_token = custom_token_bytes.decode("utf-8") if isinstance(custom_token_bytes, bytes) else custom_token_bytes
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_WEB_API_KEY}"
    resp = requests.post(verify_url, json={"token": custom_token, "returnSecureToken": True}, timeout=15)
    id_token = resp.json()["idToken"]
    print(f"[2. ID TOKEN] Acquired authentic token: {id_token[:20]}... (length: {len(id_token)})")

    headers = {"Authorization": f"Bearer {id_token}"}

    # Upload real image
    test_img = os.path.join(BASE_DIR, "test_dental_image.jpg")
    with open(test_img, "rb") as f:
        img_bytes = f.read()

    print(f"\n[3. POST /analysis/upload] Uploading clinical image...")
    up_resp = requests.post(
        f"{API_BASE_URL}/analysis/upload",
        headers=headers,
        files={"file": ("clinical_opg.jpg", img_bytes, "image/jpeg")},
        timeout=60
    )
    assert up_resp.status_code == 200, f"Upload failed: {up_resp.text}"
    upload_id = up_resp.json()["upload_id"]
    image_url = up_resp.json()["image_url"]
    print(f"   -> upload_id: {upload_id}")
    print(f"   -> image_url: {image_url}")

    # Run Analysis
    print(f"\n[4. POST /analysis/analyze] Running AI inference and atomic persistence...")
    an_resp = requests.post(
        f"{API_BASE_URL}/analysis/analyze",
        headers=headers,
        data={
            "upload_id": upload_id,
            "patient_name": "Navitha Clinical Patient",
            "view_type": "frontal",
            "dob": "1998-07-20",
            "gender": "Female"
        },
        timeout=180
    )
    assert an_resp.status_code == 200, f"Analyze failed: {an_resp.text}"
    report = an_resp.json()
    case_id = report.get("id") or report.get("case_id")
    print(f"   -> canonical case_id: {case_id}")
    print(f"   -> patient_name: {report.get('patient_name')}")
    print(f"   -> overallScore: {report.get('overallScore')}")
    print(f"   -> abo_score: {report.get('abo_score')}")
    print(f"   -> andrews_score: {report.get('andrews_score')}")
    print(f"   -> confidence_score: {report.get('confidence_score')}")

    # Direct Cloud Firestore Verification
    db = get_firestore_client()
    user_case_ref = db.collection("users").document(uid).collection("cases").document(case_id).get()
    root_case_ref = db.collection("cases").document(case_id).get()
    root_report_ref = db.collection("analysis_reports").document(case_id).get()

    print(f"\n[5. FIRESTORE PERSISTENCE VERIFICATION]")
    print(f"   -> users/{uid}/cases/{case_id} exists: {user_case_ref.exists}")
    print(f"   -> cases/{case_id} exists: {root_case_ref.exists}")
    print(f"   -> analysis_reports/{case_id} exists: {root_report_ref.exists}")

    if user_case_ref.exists:
        uc_data = user_case_ref.to_dict()
        print(f"   -> Stored Document status: {uc_data.get('status')}, overall_score: {uc_data.get('overall_score')}")

    # GET /analysis/history
    print(f"\n[6. GET /analysis/history]")
    hist_resp = requests.get(f"{API_BASE_URL}/analysis/history", headers=headers, timeout=30)
    assert hist_resp.status_code == 200
    hist_list = hist_resp.json()
    print(f"   -> Total cases returned: {len(hist_list)}")
    for h in hist_list:
        print(f"      Case {h.get('id')} | Patient: {h.get('patient_name')} | Score: {h.get('overallScore') or h.get('finishing_score')} | Created: {h.get('created_at')}")

    # GET /analysis/report/{case_id}
    print(f"\n[7. GET /analysis/report/{case_id}]")
    rep_resp = requests.get(f"{API_BASE_URL}/analysis/report/{case_id}", headers=headers, timeout=30)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    print(f"   -> Reopened report ID: {rep_data.get('id')}")
    print(f"   -> Reopened patient_name: {rep_data.get('patient_name')}")
    print(f"   -> Reopened overallScore: {rep_data.get('overallScore')}")
    print(f"   -> Reopened image_url: {rep_data.get('image_url')}")

    print("\n" + "=" * 80)
    print("ALL TRACE STEPS FOR navithaselvam07@gmail.com COMPLETED AND VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    run_navitha_trace()
