import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
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

print("==================================================================")
print(f"MIGRATING FIRESTORE DATA FROM OLD UID: {OLD_UID} -> ACTIVE UID: {NEW_UID}")
print("==================================================================")

# 1. Fetch old user profile data
old_user_ref = db.collection("users").document(OLD_UID)
old_user_doc = old_user_ref.get()
old_user_data = old_user_doc.to_dict() if old_user_doc.exists else {}

# 2. Fetch and migrate cases subcollection
old_cases_ref = old_user_ref.collection("cases")
old_cases = list(old_cases_ref.stream())
print(f"Found {len(old_cases)} case(s) in {OLD_UID}/cases:")

migrated_count = 0
for c_doc in old_cases:
    c_data = c_doc.to_dict()
    c_id = c_doc.id
    print(f"  Migrating case {c_id} ('{c_data.get('patient_name')}') ...")
    
    # Update ownership fields
    c_data["user_id"] = NEW_UID
    c_data["userId"] = NEW_UID
    c_data["doctor_id"] = NEW_UID
    c_data["doctorId"] = NEW_UID
    c_data["email"] = USER_EMAIL
    c_data["doctor_email"] = USER_EMAIL
    c_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Write to new user's subcollection
    db.collection("users").document(NEW_UID).collection("cases").document(c_id).set(c_data, merge=True)
    
    # Write/Update to root 'cases'
    db.collection("cases").document(c_id).set(c_data, merge=True)
    
    # Write/Update to root 'analysis_reports'
    db.collection("analysis_reports").document(c_id).set(c_data, merge=True)
    
    # Write/Update to root 'analyses'
    db.collection("analyses").document(c_id).set(c_data, merge=True)
    
    # Delete from old subcollection
    c_doc.reference.delete()
    migrated_count += 1
    print(f"    -> Successfully migrated to users/{NEW_UID}/cases/{c_id} and root collections.")

# 3. Update root collections for any other orphaned docs referencing OLD_UID
for col_name in ["cases", "analysis_reports", "analyses"]:
    for doc in db.collection(col_name).stream():
        d = doc.to_dict()
        uid = d.get("user_id") or d.get("userId") or d.get("doctor_id") or d.get("doctorId")
        if uid == OLD_UID:
            print(f"  Updating orphaned {col_name}/{doc.id} ownership to {NEW_UID}...")
            doc.reference.set({
                "user_id": NEW_UID,
                "userId": NEW_UID,
                "doctor_id": NEW_UID,
                "doctorId": NEW_UID,
                "email": USER_EMAIL,
                "doctor_email": USER_EMAIL
            }, merge=True)

# 4. Count total cases for new user
new_cases = list(db.collection("users").document(NEW_UID).collection("cases").stream())
total_cases_count = len(new_cases)

# 5. Update new user profile
new_user_ref = db.collection("users").document(NEW_UID)
new_user_data = {
    "uid": NEW_UID,
    "email": USER_EMAIL,
    "display_name": old_user_data.get("display_name") or "navi",
    "role": old_user_data.get("role") or "doctor",
    "total_cases": total_cases_count,
    "last_active": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}
new_user_ref.set(new_user_data, merge=True)
print(f"Updated user doc {NEW_UID}: {new_user_data}")

# 6. Delete old user document
if old_user_doc.exists:
    old_user_ref.delete()
    print(f"Deleted legacy user doc: {OLD_UID}")

print("==================================================================")
print(f"MIGRATION COMPLETE: {migrated_count} case(s) unified under {NEW_UID}")
print("==================================================================")
