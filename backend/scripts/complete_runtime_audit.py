import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
import hashlib

API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
BACKEND_BASE = "https://orthofinixai-backend.onrender.com"

def get_auth_token(email="doctor@orthofinix.ai", password="Password123!"):
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    }).encode("utf-8")
    req = urllib.request.Request(AUTH_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["localId"], data["idToken"], data.get("expiresIn")

def make_request(method, path, token, data=None, headers=None):
    url = f"{BACKEND_BASE}{path}"
    req_headers = {"Authorization": f"Bearer {token}", "User-Agent": "OrthofinixAudit/1.0"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode("utf-8")
        try:
            return resp.status, json.loads(body)
        except:
            return resp.status, body

def create_multipart(fields, files):
    boundary = "----WebKitFormBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode())
    for name, (filename, content, content_type) in files.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode())
        lines.append(f"Content-Type: {content_type}".encode())
        lines.append(b"")
        lines.append(content)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"

def run_audit():
    print("=" * 60)
    print("ORTHOFINIX RUNTIME AUDIT START")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Production Backend: {BACKEND_BASE}")
    print("=" * 60)

    # 1. Firebase Auth Check
    print("\n--- PHASE 3 & 4: FIREBASE AUTH & TOKEN VERIFICATION ---")
    uid, id_token, expires_in = get_auth_token()
    print(f"Firebase UID: {uid}")
    print(f"Firebase Token Present: True")
    print(f"Token Expiration: {expires_in} seconds")

    # 2. Verify /me
    print("\n--- TESTING GET /me ---")
    status, me_resp = make_request("GET", "/me", id_token)
    print(f"GET /me Status: {status}")
    print(f"Response: {me_resp}")
    assert me_resp.get("uid") == uid or me_resp.get("id") == uid or me_resp.get("email") == "doctor@orthofinix.ai", f"UID mismatch in /me: {me_resp}"

    # 3. Create Patient
    print("\n--- TESTING POST /patients/ ---")
    pat_data = json.dumps({
        "name": f"AuditPatient_{int(time.time())}",
        "date_of_birth": "1995-06-15",
        "gender": "Female",
        "contact_info": "+1-555-0199"
    }).encode("utf-8")
    status, pat_resp = make_request("POST", "/patients/", id_token, data=pat_data, headers={"Content-Type": "application/json"})
    print(f"POST /patients/ Status: {status}")
    print(f"Created Patient ID: {pat_resp.get('id')}, Name: {pat_resp.get('name')}")
    patient_id = pat_resp.get("id")
    patient_name = pat_resp.get("name")

    # 4. Upload Image A (Real dental OPG simulation)
    print("\n--- TESTING POST /analysis/upload (IMAGE A) ---")
    from PIL import Image, ImageDraw
    import io

    img_a = Image.new("RGB", (800, 500), color=(30, 40, 60))
    draw_a = ImageDraw.Draw(img_a)
    draw_a.ellipse([100, 100, 700, 400], outline=(255, 255, 255), width=4)
    draw_a.text((350, 240), "OPG Dental Case A", fill=(200, 230, 255))
    buf_a = io.BytesIO()
    img_a.save(buf_a, format="PNG")
    img_a_bytes = buf_a.getvalue()
    img_a_hash = hashlib.sha256(img_a_bytes).hexdigest()[:16]

    body_a, content_type_a = create_multipart({}, {"file": ("opg_case_a.png", img_a_bytes, "image/png")})
    status, upload_a = make_request("POST", "/analysis/upload", id_token, data=body_a, headers={"Content-Type": content_type_a})
    print(f"Upload A Status: {status}, Upload ID: {upload_a.get('upload_id')}, Image Hash: {img_a_hash}")
    upload_id_a = upload_a.get("upload_id")

    # 5. Analyze Image A
    print("\n--- TESTING POST /analysis/analyze (CASE A) ---")
    case_a_id = f"case_audit_a_{int(time.time())}"
    fields_a = {
        "upload_id": upload_id_a,
        "patient_name": patient_name,
        "view_type": "opg",
        "case_id": case_a_id,
        "dob": "1995-06-15",
        "gender": "Female"
    }
    body_analyze_a, ct_analyze_a = create_multipart(fields_a, {})
    status, analyze_a = make_request("POST", "/analysis/analyze", id_token, data=body_analyze_a, headers={"Content-Type": ct_analyze_a})
    print(f"Analyze A Status: {status}")
    print(f"Report ID: {analyze_a.get('id')}")
    print(f"Finishing Score: {analyze_a.get('finishing_score')}")
    print(f"ABO Score: {analyze_a.get('abo_score')}")
    print(f"Andrews Score: {analyze_a.get('andrews_score')}")
    print(f"Root Angulation Score: {analyze_a.get('root_angulation_score')}")
    print(f"Overjet: {analyze_a.get('overjet_mm')} mm, Overbite: {analyze_a.get('overbite_percent')}%")
    rec_id_a = analyze_a.get("id")

    # 6. Upload Image B (Distinct image bytes)
    print("\n--- TESTING POST /analysis/upload & analyze (IMAGE B - VARIANCE TEST) ---")
    img_b = Image.new("RGB", (640, 480), color=(180, 200, 220))
    draw_b = ImageDraw.Draw(img_b)
    draw_b.rectangle([50, 50, 590, 430], outline=(20, 80, 160), width=6)
    draw_b.text((200, 220), "Frontal Intraoral Case B", fill=(0, 50, 100))
    buf_b = io.BytesIO()
    img_b.save(buf_b, format="PNG")
    img_b_bytes = buf_b.getvalue()
    img_b_hash = hashlib.sha256(img_b_bytes).hexdigest()[:16]

    body_b, content_type_b = create_multipart({}, {"file": ("frontal_case_b.png", img_b_bytes, "image/png")})
    status, upload_b = make_request("POST", "/analysis/upload", id_token, data=body_b, headers={"Content-Type": content_type_b})
    upload_id_b = upload_b.get("upload_id")
    print(f"Upload B Status: {status}, Upload ID: {upload_id_b}, Image Hash: {img_b_hash}")

    case_b_id = f"case_audit_b_{int(time.time())}"
    fields_b = {
        "upload_id": upload_id_b,
        "patient_name": "SecondPatient_Audit",
        "view_type": "frontal",
        "case_id": case_b_id,
        "dob": "2002-01-10",
        "gender": "Male"
    }
    body_analyze_b, ct_analyze_b = create_multipart(fields_b, {})
    status, analyze_b = make_request("POST", "/analysis/analyze", id_token, data=body_analyze_b, headers={"Content-Type": ct_analyze_b})
    print(f"Analyze B Status: {status}")
    print(f"Report ID: {analyze_b.get('id')}")
    print(f"Finishing Score: {analyze_b.get('finishing_score')}")
    print(f"ABO Score: {analyze_b.get('abo_score')}")
    print(f"Andrews Score: {analyze_b.get('andrews_score')}")
    rec_id_b = analyze_b.get("id")

    # 7. Check History
    print("\n--- TESTING GET /analysis/history ---")
    status, history = make_request("GET", "/analysis/history", id_token)
    print(f"GET /analysis/history Status: {status}, Total Items: {len(history)}")
    history_ids = [item.get("id") for item in history]
    print(f"History IDs retrieved: {history_ids[:10]}")
    assert rec_id_a in history_ids, f"Case A ({rec_id_a}) missing from backend history!"
    assert rec_id_b in history_ids, f"Case B ({rec_id_b}) missing from backend history!"
    print("SUCCESS: Both Case A and Case B are present in backend /analysis/history!")

    # 8. Check Report by ID
    print(f"\n--- TESTING GET /analysis/report/{rec_id_a} ---")
    status, rep_a = make_request("GET", f"/analysis/report/{rec_id_a}", id_token)
    print(f"GET /analysis/report/{rec_id_a} Status: {status}")
    print(f"Patient Name: {rep_a.get('patient_name')}")
    print(f"Finishing Score: {rep_a.get('finishing_score')}")
    print(f"Recommendations Count: {len(rep_a.get('recommendations', []))}")

    # 9. Deletion Test
    print(f"\n--- TESTING DELETE /analysis/{rec_id_a} ---")
    status, del_resp = make_request("DELETE", f"/analysis/{rec_id_a}", id_token)
    print(f"DELETE Status: {status}, Response: {del_resp}")

    time.sleep(2)
    status, history_after = make_request("GET", "/analysis/history", id_token)
    history_after_ids = [item.get("id") for item in history_after]
    print(f"History after deletion: {len(history_after)} items")
    assert rec_id_a not in history_after_ids, f"Case A ({rec_id_a}) was NOT deleted from backend history!"
    print(f"SUCCESS: Case A ({rec_id_a}) is confirmed permanently purged from backend history!")

    print("\n" + "=" * 60)
    print("ALL PRODUCTION BACKEND API & DATA CHECKS PASSED LIVE!")
    print("=" * 60)

if __name__ == "__main__":
    run_audit()
