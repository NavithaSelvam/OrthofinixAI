import firebase_admin
from firebase_admin import credentials, firestore
import os

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

OLD_UID = "7MkC6E7TVFWLiktcrN9ZwQANnQr2"
NEW_UID = "ArYEcygXQ8W9ZecRUQbfpqTDQK92"
USER_EMAIL = "navithselvam07@gmail.com"

print(f"=== INSPECTION BEFORE MIGRATION ===")
old_user_doc = db.collection("users").document(OLD_UID).get()
print(f"Old user doc ({OLD_UID}) exists: {old_user_doc.exists}")
if old_user_doc.exists:
    print(f"  Old user data: {old_user_doc.to_dict()}")

new_user_doc = db.collection("users").document(NEW_UID).get()
print(f"New user doc ({NEW_UID}) exists: {new_user_doc.exists}")
if new_user_doc.exists:
    print(f"  New user data: {new_user_doc.to_dict()}")

old_subcases = list(db.collection("users").document(OLD_UID).collection("cases").stream())
print(f"Old subcollection cases count: {len(old_subcases)}")
for c in old_subcases:
    print(f"  Case ID: {c.id}, data: {c.to_dict().get('patient_name')}")

new_subcases = list(db.collection("users").document(NEW_UID).collection("cases").stream())
print(f"New subcollection cases count: {len(new_subcases)}")
for c in new_subcases:
    print(f"  Case ID: {c.id}, data: {c.to_dict().get('patient_name')}")

root_cases = list(db.collection("cases").stream())
print(f"Total root cases: {len(root_cases)}")
for rc in root_cases:
    d = rc.to_dict()
    u = d.get("user_id") or d.get("userId")
    em = d.get("email") or d.get("doctor_email")
    if u in [OLD_UID, NEW_UID] or em == USER_EMAIL:
        print(f"  Root Case ID: {rc.id} | UID: {u} | Email: {em} | Patient: {d.get('patient_name')}")
