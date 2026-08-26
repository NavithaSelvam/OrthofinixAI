import firebase_admin
from firebase_admin import credentials, firestore
import json

cred_path = "backend/firebase-adminsdk.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

OLD_UID = "7MkC6E7TVFWLiktcrN9ZwQANnQr2"
NEW_UID = "ArYEcygXQ8W9ZecRUQbfpqTDQK92"
USER_EMAIL = "navithselvam07@gmail.com"

print("--- Checking all collections for OLD_UID / Case OF-2026-6934 ---")

# 1. Subcollection case
doc = db.collection("users").document(OLD_UID).collection("cases").document("OF-2026-6934").get()
print(f"Subcollection doc OF-2026-6934 exists: {doc.exists}")
if doc.exists:
    print(f"Data: {json.dumps(doc.to_dict(), default=str, indent=2)}")

# 2. Root cases
for col_name in ["cases", "analysis_reports", "analyses", "patients", "images"]:
    col = db.collection(col_name)
    docs = list(col.stream())
    print(f"\nCollection '{col_name}' total docs: {len(docs)}")
    for d in docs:
        data = d.to_dict()
        uid = data.get("user_id") or data.get("userId") or data.get("doctor_id") or data.get("doctorId")
        email = data.get("email") or data.get("doctor_email")
        if uid in [OLD_UID, NEW_UID] or email == USER_EMAIL or d.id == "OF-2026-6934":
            print(f"  Doc ID: {d.id} | UID: {uid} | Email: {email} | Summary: {data.get('patient_name') or data.get('name')}")
