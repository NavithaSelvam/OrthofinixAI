import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

AUTHENTIC_UIDS = {
    "ArYEcygXQ8W9ZecRUQbfpqTDQK92",  # navithselvam07@gmail.com
    "S5LbWcrbC0ZnZVZS5hvBGFYvLfz2",  # navithaselvam07@gmail.com
    "ve5yom41VhOi92Ipup3hiOq8jM73",  # doctor@orthofinix.ai
    "YpC45yYkPmPioe69576OYnBGtHF3",
    "Cc99ha47rnhM1JE822Q7OiWv7mO2",
    "Z8Pr2Q0UDmZUJpaFcaqOKXLSM773",
    "bm1GEtpao5NbjbkkK8q7c8kY4di1"
}

GHOST_PREFIXES = [
    "doctor_",
    "doc_",
    "firebase_user_",
    "test_doc_",
    "dr_prod_user_",
    "eeaeb1b8-"
]

SPECIAL_CHECK_UIDS = [
    "6wjsn8MB25PvDdavReMmqtFgUA92"
]

def recursively_delete_doc(doc_ref):
    """
    Recursively deletes all subcollections and the document itself.
    """
    try:
        # Check subcollections
        for sub_col in doc_ref.collections():
            for sub_doc in sub_col.stream():
                recursively_delete_doc(sub_doc.reference)
        doc_ref.delete()
    except Exception as e:
        print(f"Error recursively deleting {doc_ref.path}: {e}")

print("=" * 80)
print("PURGING ORPHANED / GHOST USERS AND SYNTHETIC COLLECTIONS FROM CLOUD FIRESTORE")
print("=" * 80)

# 1. Inspect and Purge 'users' Collection
print("\n[1] Scanning 'users' collection...")
user_docs = list(db.collection("users").stream())
deleted_users = 0
retained_users = []

for u_doc in user_docs:
    uid = u_doc.id
    u_data = u_doc.to_dict() or {}
    
    # Check if legitimate
    if uid in AUTHENTIC_UIDS:
        retained_users.append((uid, u_data.get("email", "No Email"), u_data.get("display_name", "Doctor")))
        continue
    
    should_delete = False
    
    # Check ghost prefixes
    for prefix in GHOST_PREFIXES:
        if uid.startswith(prefix):
            should_delete = True
            break
            
    # Check special UIDs
    if uid in SPECIAL_CHECK_UIDS:
        # Check if empty (no cases or empty fields)
        sub_cases = list(u_doc.reference.collection("cases").limit(1).stream())
        if not sub_cases and not u_data.get("email"):
            should_delete = True
        elif not sub_cases:
            should_delete = True

    # If not in AUTHENTIC_UIDS and has dummy-like traits
    if not should_delete and uid not in AUTHENTIC_UIDS:
        # If it doesn't match any legitimate format or is an orphaned test ID
        email = u_data.get("email", "")
        if "test" in uid.lower() or "dummy" in uid.lower() or "test" in email.lower() or not email:
            should_delete = True

    if should_delete:
        print(f"  -> [RECURSIVE DELETE] users/{uid} (Email: {u_data.get('email', 'None')})")
        recursively_delete_doc(u_doc.reference)
        deleted_users += 1

print(f"Deleted {deleted_users} synthetic/ghost user document(s).")
print(f"Retained {len(retained_users)} authentic user document(s):")
for r_uid, r_email, r_name in retained_users:
    print(f"  * {r_uid} | {r_email} | {r_name}")

# 2. Inspect and Purge root collections ('cases', 'analyses', 'analysis_reports', 'patients', 'images')
root_collections = ["cases", "analyses", "analysis_reports", "patients", "images"]
total_root_deleted = 0

for coll_name in root_collections:
    print(f"\n[2] Scanning root collection '{coll_name}' for ghost records...")
    docs = list(db.collection(coll_name).stream())
    coll_deleted = 0
    for doc in docs:
        d = doc.to_dict() or {}
        doc_id = doc.id
        owner_uid = d.get("user_id") or d.get("userId") or d.get("doctor_id") or d.get("doctorId") or ""
        email = d.get("email") or d.get("doctor_email") or ""
        
        is_ghost = False
        for prefix in GHOST_PREFIXES:
            if owner_uid.startswith(prefix) or doc_id.startswith(prefix):
                is_ghost = True
                break
                
        if owner_uid in SPECIAL_CHECK_UIDS or "test" in owner_uid.lower() or "dummy" in owner_uid.lower():
            is_ghost = True

        if is_ghost:
            print(f"  -> [DELETE] {coll_name}/{doc_id} (Owner UID: {owner_uid})")
            recursively_delete_doc(doc.reference)
            coll_deleted += 1
            total_root_deleted += 1
            
    print(f"Finished '{coll_name}': {coll_deleted} ghost document(s) deleted.")

# 3. Final Verification of 'users' collection
print("\n" + "=" * 80)
print("FINAL VERIFICATION OF 'users' COLLECTION VIA FIRESTORE STREAM")
print("=" * 80)
final_users = list(db.collection("users").stream())
print(f"Total remaining users in Firestore: {len(final_users)}")
all_valid = True
for fu in final_users:
    fuid = fu.id
    fdata = fu.to_dict() or {}
    status = "[AUTHENTIC]" if fuid in AUTHENTIC_UIDS else "[UNKNOWN]"
    if fuid not in AUTHENTIC_UIDS:
        all_valid = False
    print(f"  {status} UID: {fuid} | Email: {fdata.get('email', 'N/A')} | Cases: {fdata.get('total_cases', 0)}")

print("=" * 80)
if all_valid:
    print("VERIFICATION SUCCESSFUL: ONLY AUTHENTIC USER DOCUMENTS REMAIN IN FIRESTORE!")
else:
    print("WARNING: Some unknown user documents remain.")
print("=" * 80)
