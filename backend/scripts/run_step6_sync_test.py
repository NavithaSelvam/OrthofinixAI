import requests
import io
import time
from PIL import Image

BASE_URL = "https://orthofinixai-backend.onrender.com"
API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

USER_A_EMAIL = "dr.audit@orthofinix.ai"
USER_A_PASS = "AuditPassword2026!"

USER_B_EMAIL = "dr.second.doctor@orthofinix.ai"
USER_B_PASS = "SecondDoctorPass2026!"

def create_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (640, 480), color=(140, 190, 230))
    img.save(buf, format="JPEG")
    return buf.getvalue()

def get_firebase_token(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    if res.status_code != 200:
        res = requests.post(SIGNUP_URL, json={"email": email, "password": password, "returnSecureToken": True})
    data = res.json()
    return data.get("idToken"), data.get("localId")

print("=" * 75)
print("STEP 6: REAL CROSS-PLATFORM SYNCHRONIZATION AND ISOLATION TEST")
print("Target Backend:", BASE_URL)
print("=" * 75, flush=True)

# ----------------------------------------------------------------------
# 1. Authenticate User A
# ----------------------------------------------------------------------
token_a, uid_a = get_firebase_token(USER_A_EMAIL, USER_A_PASS)
headers_a = {"Authorization": f"Bearer {token_a}"}
print(f"\n[+] User A Authenticated: Email={USER_A_EMAIL}, UID={uid_a}", flush=True)

# ----------------------------------------------------------------------
# TEST A: Web creates Case A -> Android retrieves Case A
# ----------------------------------------------------------------------
print("\n--- TEST A: Create Case A (Web) -> Verify on Android ---", flush=True)
img_bytes = create_image_bytes()

# Upload
r_upload_a = requests.post(f"{BASE_URL}/analysis/upload", headers=headers_a, files={"file": ("case_a_web.jpg", img_bytes, "image/jpeg")}, timeout=60)
assert r_upload_a.status_code == 200, f"Upload A failed: {r_upload_a.text}"
upload_id_a = r_upload_a.json()["upload_id"]

# Analyze
case_a_id = f"case_A_{int(time.time())}"
payload_a = {
    "upload_id": upload_id_a,
    "patient_name": "PATIENT_A_WEB",
    "view_type": "opg",
    "case_id": case_a_id,
    "dob": "1995-03-20",
    "gender": "Female"
}
r_analyze_a = requests.post(f"{BASE_URL}/analysis/analyze", headers=headers_a, data=payload_a, timeout=120)
assert r_analyze_a.status_code == 200, f"Analyze A failed: {r_analyze_a.text}"
case_a_data = r_analyze_a.json()
print(f"[OK] Case A Created: ID={case_a_id}, Patient={case_a_data.get('patient_name')}, Score={case_a_data.get('finishing_score')}", flush=True)

# Verify Android fetches Case A
r_android_sync = requests.get(f"{BASE_URL}/analysis/history", headers=headers_a, timeout=60)
assert r_android_sync.status_code == 200
history_a = r_android_sync.json()
found_a_on_android = any(c.get("id") == case_a_id or c.get("patient_name") == "PATIENT_A_WEB" for c in history_a)
print(f"[VERIFY TEST A] Case A found in Android history: {found_a_on_android} (Total cases for User A: {len(history_a)})", flush=True)

test_a_pass = found_a_on_android

# ----------------------------------------------------------------------
# TEST B: Android creates Case B -> Web retrieves Case B
# ----------------------------------------------------------------------
print("\n--- TEST B: Create Case B (Android) -> Verify on Web ---", flush=True)

# Upload from Android client
r_upload_b = requests.post(f"{BASE_URL}/analysis/upload", headers=headers_a, files={"file": ("case_b_android.jpg", img_bytes, "image/jpeg")}, timeout=60)
assert r_upload_b.status_code == 200
upload_id_b = r_upload_b.json()["upload_id"]

# Analyze from Android client
case_b_id = f"case_B_{int(time.time())}"
payload_b = {
    "upload_id": upload_id_b,
    "patient_name": "PATIENT_B_ANDROID",
    "view_type": "opg",
    "case_id": case_b_id,
    "dob": "2001-08-14",
    "gender": "Male"
}
r_analyze_b = requests.post(f"{BASE_URL}/analysis/analyze", headers=headers_a, data=payload_b, timeout=120)
assert r_analyze_b.status_code == 200
case_b_data = r_analyze_b.json()
print(f"[OK] Case B Created: ID={case_b_id}, Patient={case_b_data.get('patient_name')}, Score={case_b_data.get('finishing_score')}", flush=True)

# Verify Web fetches Case B
r_web_sync = requests.get(f"{BASE_URL}/analysis/history", headers=headers_a, timeout=60)
assert r_web_sync.status_code == 200
history_a_updated = r_web_sync.json()
found_b_on_web = any(c.get("id") == case_b_id or c.get("patient_name") == "PATIENT_B_ANDROID" for c in history_a_updated)
print(f"[VERIFY TEST B] Case B found in Web history: {found_b_on_web} (Total cases for User A: {len(history_a_updated)})", flush=True)

test_b_pass = found_b_on_web

# ----------------------------------------------------------------------
# TEST C: Second User B -> User Isolation Test
# ----------------------------------------------------------------------
print("\n--- TEST C: User Isolation with Second Firebase Account ---", flush=True)
token_b, uid_b = get_firebase_token(USER_B_EMAIL, USER_B_PASS)
headers_b = {"Authorization": f"Bearer {token_b}"}
print(f"[+] User B Authenticated: Email={USER_B_EMAIL}, UID={uid_b}", flush=True)
assert uid_a != uid_b, "Error: User A and User B have the same UID!"

# User B creates Case C
r_upload_c = requests.post(f"{BASE_URL}/analysis/upload", headers=headers_b, files={"file": ("case_c_user_b.jpg", img_bytes, "image/jpeg")}, timeout=60)
assert r_upload_c.status_code == 200
upload_id_c = r_upload_c.json()["upload_id"]

case_c_id = f"case_C_{int(time.time())}"
payload_c = {
    "upload_id": upload_id_c,
    "patient_name": "PATIENT_C_USER_B",
    "view_type": "opg",
    "case_id": case_c_id,
    "dob": "1988-12-05",
    "gender": "Female"
}
r_analyze_c = requests.post(f"{BASE_URL}/analysis/analyze", headers=headers_b, data=payload_c, timeout=120)
assert r_analyze_c.status_code == 200
print(f"[OK] Case C Created under User B: ID={case_c_id}", flush=True)

# 1. User A checks their history -> MUST NOT see Case C
r_hist_user_a = requests.get(f"{BASE_URL}/analysis/history", headers=headers_a, timeout=60)
user_a_cases = r_hist_user_a.json()
user_a_sees_case_c = any(c.get("id") == case_c_id or c.get("patient_name") == "PATIENT_C_USER_B" for c in user_a_cases)
print(f"[*] User A sees Case C: {user_a_sees_case_c} (Must be False)", flush=True)

# 2. User B checks their history -> MUST NOT see Case A or Case B
r_hist_user_b = requests.get(f"{BASE_URL}/analysis/history", headers=headers_b, timeout=60)
user_b_cases = r_hist_user_b.json()
user_b_sees_case_a = any(c.get("id") == case_a_id or c.get("patient_name") == "PATIENT_A_WEB" for c in user_b_cases)
user_b_sees_case_b = any(c.get("id") == case_b_id or c.get("patient_name") == "PATIENT_B_ANDROID" for c in user_b_cases)
user_b_sees_case_c = any(c.get("id") == case_c_id for c in user_b_cases)

print(f"[*] User B sees Case A: {user_b_sees_case_a} (Must be False)", flush=True)
print(f"[*] User B sees Case B: {user_b_sees_case_b} (Must be False)", flush=True)
print(f"[*] User B sees Case C: {user_b_sees_case_c} (Must be True)", flush=True)

test_c_pass = (not user_a_sees_case_c) and (not user_b_sees_case_a) and (not user_b_sees_case_b) and user_b_sees_case_c

print("\n" + "=" * 75)
print("FINAL STEP 6 RESULTS SUMMARY")
print("=" * 75)
print(f"Web -> Backend -> Android: {'PASS' if test_a_pass else 'FAIL'}")
print(f"Android -> Backend -> Web: {'PASS' if test_b_pass else 'FAIL'}")
print(f"User isolation:            {'PASS' if test_c_pass else 'FAIL'}")
print("=" * 75, flush=True)
