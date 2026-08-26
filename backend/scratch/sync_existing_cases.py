import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=== SYNCING CASE OF-2026-6934 TO ALL RELEVANT USER ACCOUNTS & ROOT COLLECTIONS ===")
source_doc = db.collection("users").document("S5LbWcrbC0ZnZVZS5hvBGFYvLfz2").collection("cases").document("OF-2026-6934").get()

if source_doc.exists:
    case_data = source_doc.to_dict() or {}
    print("Found case_data:", case_data)
    
    # Save to root 'cases'
    db.collection("cases").document("OF-2026-6934").set(case_data, merge=True)
    # Save to root 'analysis_reports'
    db.collection("analysis_reports").document("OF-2026-6934").set(case_data, merge=True)
    # Save to root 'analyses'
    db.collection("analyses").document("OF-2026-6934").set(case_data, merge=True)
    
    # Find all user accounts matching doctor's email
    users = list(db.collection("users").stream())
    target_uids = ["7MkC6E7TVFWLiktcrN9ZwQANnQr2", "Cc99ha47rnhM1JE822Q7OiWv7mO2", "S5LbWcrbC0ZnZVZS5hvBGFYvLfz2", "eeaeb1b8-98c2-4e42-b8e3-2fd3b3e125aa"]
    for u in users:
        udata = u.to_dict() or {}
        email = udata.get("email") or ""
        if "navitha" in email.lower() or u.id in target_uids:
            print(f"Syncing case to user {u.id} ({email})...")
            db.collection("users").document(u.id).collection("cases").document("OF-2026-6934").set(case_data, merge=True)
            db.collection("users").document(u.id).update({"total_cases": 1})
            
    print("SUCCESS: Case synchronized across all collections!")
else:
    print("Case not found in source doc!")
