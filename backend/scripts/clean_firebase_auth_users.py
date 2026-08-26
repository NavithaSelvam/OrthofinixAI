import os
import sys
import firebase_admin
from firebase_admin import credentials, auth, firestore

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

ALLOWED_EMAILS = {
    "navithselvam07@gmail.com",
    "navithaselvam07@gmail.com",
    "doctor@orthofinix.ai",
    "kanimozhis.sse@saveetha.com",
    "navithas1080.sse@saveetha.com"
}

ALLOWED_UIDS = {
    "ArYEcygXQ8W9ZecRUQbfpqTDQK92",
    "S5LbWcrbC0ZnZVZS5hvBGFYvLfz2",
    "Cc99ha47rnhM1JE822Q7OiWv7mO2",
    "ve5yom41VhOi92Ipup3hiOq8jM73",
    "YpC45yYkPmPioe69576OYnBGtHF3",
    "Z8Pr2Q0UDmZUJpaFcaqOKXLSM773",
    "bm1GEtpao5NbjbkkK8q7c8kY4di1"
}

print("=" * 80)
print("FIREBASE AUTHENTICATION CLEANUP — PURGING SYNTHETIC & TEST ACCOUNTS")
print("=" * 80)

# List all users in Firebase Auth
page = auth.list_users()
deleted_count = 0
retained_count = 0

while page:
    for user in page.users:
        uid = user.uid
        email = (user.email or "").lower().strip()
        
        is_allowed = False
        if uid in ALLOWED_UIDS or email in ALLOWED_EMAILS:
            is_allowed = True
            
        if is_allowed:
            print(f"[RETAIN] Auth User: UID={uid} | Email={email} | Name={user.display_name}")
            retained_count += 1
        else:
            print(f"[DELETE AUTH USER] UID={uid} | Email={email}")
            try:
                auth.delete_user(uid)
                # Also delete from Firestore if exists
                db.collection("users").document(uid).delete()
                deleted_count += 1
            except Exception as err:
                print(f"  Error deleting user {uid}: {err}")
                
    page = page.get_next_page()

print("=" * 80)
print(f"FIREBASE AUTH PURGE COMPLETE!")
print(f"Deleted Synthetic Users: {deleted_count}")
print(f"Retained Legitimate Users: {retained_count}")
print("=" * 80)
