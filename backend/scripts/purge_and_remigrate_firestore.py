import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

ACTIVE_UIDS = {
    "ArYEcygXQ8W9ZecRUQbfpqTDQK92": "navithselvam07@gmail.com",
    "S5LbWcrbC0ZnZVZS5hvBGFYvLfz2": "navithselvam07@gmail.com"
}
PRIMARY_UID = "ArYEcygXQ8W9ZecRUQbfpqTDQK92"
PRIMARY_EMAIL = "navithselvam07@gmail.com"

DUMMY_UID_PREFIXES = [
    "firebase_user_a_uid_",
    "firebase_user_b_uid_",
    "test_doc_",
    "doctor_alpha_",
    "doctor_dynamic_",
    "dr_prod_user_",
    "demo_doctor_",
    "anonymous_doctor"
]

def is_dummy_uid(uid_val: str) -> bool:
    if not uid_val:
        return False
    u = str(uid_val).strip()
    if u in ACTIVE_UIDS:
        return False
    for p in DUMMY_UID_PREFIXES:
        if u.startswith(p) or u == p:
            return True
    return False

print("=" * 80)
print("STARTING FIRESTORE PURGE OF DUMMY RECORDS & RE-MIGRATION TO ACTIVE USER UID")
print(f"Target Active Primary UID: {PRIMARY_UID} ({PRIMARY_EMAIL})")
print("=" * 80)

# 1. Scan and clean root collections: 'cases', 'analysis_reports', 'analyses', 'patients', 'images'
collections_to_clean = ["cases", "analysis_reports", "analyses", "patients", "images"]
total_deleted = 0
total_migrated = 0

for coll_name in collections_to_clean:
    print(f"\nScanning collection '{coll_name}'...")
    docs = list(db.collection(coll_name).stream())
    deleted_in_coll = 0
    migrated_in_coll = 0
    for doc in docs:
        d = doc.to_dict()
        doc_id = doc.id
        u_id = d.get("user_id") or d.get("userId") or d.get("doctor_id") or d.get("doctorId") or ""
        doc_email = d.get("email") or d.get("doctor_email") or ""
        p_name = str(d.get("patient_name") or d.get("name") or "").lower()

        # Check if dummy test document
        if is_dummy_uid(u_id) or "test" in doc_id.lower() or "dummy" in doc_id.lower() or "audit" in doc_id.lower() or p_name.startswith("test ") or p_name == "alice cooper" or p_name == "bob anderson" or p_name == "charlie davis":
            print(f"  [DELETE] {coll_name}/{doc_id} (UID: {u_id}, Patient: {d.get('patient_name') or d.get('name')})")
            doc.reference.delete()
            deleted_in_coll += 1
            total_deleted += 1
        elif doc_email.lower() == PRIMARY_EMAIL.lower() or u_id in ACTIVE_UIDS:
            # Re-bind strictly to primary UID
            if u_id != PRIMARY_UID or d.get("user_id") != PRIMARY_UID:
                print(f"  [MIGRATE] {coll_name}/{doc_id} -> Assigning to {PRIMARY_UID}")
                d["user_id"] = PRIMARY_UID
                d["userId"] = PRIMARY_UID
                d["doctor_id"] = PRIMARY_UID
                d["doctorId"] = PRIMARY_UID
                d["email"] = PRIMARY_EMAIL
                d["doctor_email"] = PRIMARY_EMAIL
                d["updated_at"] = datetime.now(timezone.utc).isoformat()
                doc.reference.set(d, merge=True)
                migrated_in_coll += 1
                total_migrated += 1

    print(f"Finished '{coll_name}': {deleted_in_coll} deleted, {migrated_in_coll} re-linked.")

# 2. Clean dummy user documents in 'users'
print("\nScanning 'users' collection...")
user_docs = list(db.collection("users").stream())
for u_doc in user_docs:
    u_id = u_doc.id
    if is_dummy_uid(u_id):
        print(f"  [DELETE USER] users/{u_id}")
        # Delete subcollection cases first
        for sub_c in u_doc.reference.collection("cases").stream():
            sub_c.reference.delete()
        for sub_a in u_doc.reference.collection("analyses").stream():
            sub_a.reference.delete()
        u_doc.reference.delete()
        total_deleted += 1

# 3. Synchronize active user subcollection & total_cases
print(f"\nSynchronizing active user profile: users/{PRIMARY_UID}...")
active_user_ref = db.collection("users").document(PRIMARY_UID)

# Also copy from S5LbWcrbC0ZnZVZS5hvBGFYvLfz2 if it has cases
alt_uid = "S5LbWcrbC0ZnZVZS5hvBGFYvLfz2"
alt_user_ref = db.collection("users").document(alt_uid)
if alt_user_ref.get().exists:
    for sub_c in alt_user_ref.collection("cases").stream():
        c_data = sub_c.to_dict()
        c_data["user_id"] = PRIMARY_UID
        c_data["userId"] = PRIMARY_UID
        c_data["doctor_id"] = PRIMARY_UID
        c_data["doctorId"] = PRIMARY_UID
        c_data["email"] = PRIMARY_EMAIL
        c_data["doctor_email"] = PRIMARY_EMAIL
        active_user_ref.collection("cases").document(sub_c.id).set(c_data, merge=True)
        active_user_ref.collection("analyses").document(sub_c.id).set(c_data, merge=True)

# Count cases in primary user's subcollection
primary_cases = list(active_user_ref.collection("cases").stream())
total_cases_count = len(primary_cases)

# Also ensure subcollection cases are mirrored in root 'cases'
for pc in primary_cases:
    pc_data = pc.to_dict()
    pc_id = pc.id
    active_user_ref.collection("analyses").document(pc_id).set(pc_data, merge=True)
    db.collection("cases").document(pc_id).set(pc_data, merge=True)
    db.collection("analysis_reports").document(pc_id).set(pc_data, merge=True)
    db.collection("analyses").document(pc_id).set(pc_data, merge=True)

active_user_ref.set({
    "uid": PRIMARY_UID,
    "email": PRIMARY_EMAIL,
    "display_name": "navi",
    "role": "doctor",
    "total_cases": total_cases_count,
    "last_active": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}, merge=True)

print("=" * 80)
print(f"PURGE & MIGRATION COMPLETE!")
print(f"Total Deleted Dummy Documents: {total_deleted}")
print(f"Total Re-linked Documents: {total_migrated}")
print(f"Active User ({PRIMARY_UID}) Total Verified Cases: {total_cases_count}")
for c in primary_cases:
    cd = c.to_dict()
    print(f"  - Case ID: {c.id} | Patient: {cd.get('patient_name')} | Score: {cd.get('overall_score') or cd.get('finishing_score')}%")
print("=" * 80)
