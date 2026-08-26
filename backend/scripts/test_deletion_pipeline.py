import requests
import io
import time
from PIL import Image

BASE_URL = "https://orthofinixai-backend.onrender.com"
API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"
AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

USER_EMAIL = "dr.audit@orthofinix.ai"
USER_PASS = "AuditPassword2026!"

def create_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (640, 480), color=(140, 190, 230))
    img.save(buf, format="JPEG")
    return buf.getvalue()

def get_firebase_token(email, password):
    res = requests.post(AUTH_URL, json={"email": email, "password": password, "returnSecureToken": True})
    data = res.json()
    return data.get("idToken"), data.get("localId")

token, uid = get_firebase_token(USER_EMAIL, USER_PASS)
headers = {"Authorization": f"Bearer {token}"}

print(f"Testing Deletion Pipeline for UID: {uid}")

# 1. Fetch current cases
r_init = requests.get(f"{BASE_URL}/analysis/history", headers=headers)
print(f"Current cases count: {len(r_init.json())}")
for c in r_init.json():
    print(f"  Existing Case: id={c.get('id')}, case_id={c.get('case_id')}, patient={c.get('patient_name')}")

# 2. Try deleting each existing case
for c in r_init.json():
    target_id = c.get('id')
    print(f"\nDeleting case id: {target_id}...")
    r_del = requests.delete(f"{BASE_URL}/analysis/{target_id}", headers=headers)
    print(f"  DELETE status: {r_del.status_code}, body: {r_del.text}")

# 3. Check history again
r_after = requests.get(f"{BASE_URL}/analysis/history", headers=headers)
print(f"\nCases count after deletion: {len(r_after.json())}")
for c in r_after.json():
    print(f"  Remaining Case: id={c.get('id')}, case_id={c.get('case_id')}, patient={c.get('patient_name')}")
