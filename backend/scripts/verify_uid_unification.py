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
ACTIVE_UID = "ArYEcygXQ8W9ZecRUQbfpqTDQK92"
USER_EMAIL = "navithselvam07@gmail.com"

print("==================================================================")
print(f"VERIFYING UID UNIFICATION & LINKAGE FOR: {USER_EMAIL}")
print("==================================================================")

# 1. Check legacy user doc
old_doc = db.collection("users").document(OLD_UID).get()
print(f"1. Legacy doc ({OLD_UID}) exists: {old_doc.exists} (Expected: False)")

# 2. Check active user doc
active_doc = db.collection("users").document(ACTIVE_UID).get()
print(f"2. Active user doc ({ACTIVE_UID}) exists: {active_doc.exists}")
if active_doc.exists:
    d = active_doc.to_dict()
    print(f"   Email: {d.get('email')} | Display Name: {d.get('display_name')} | Total Cases: {d.get('total_cases')}")

# 3. Check active user's subcollection
active_subcases = list(db.collection("users").document(ACTIVE_UID).collection("cases").stream())
print(f"3. Active user subcollection cases count: {len(active_subcases)}")
for c in active_subcases:
    cd = c.to_dict()
    print(f"   Case ID: {c.id} | Patient: {cd.get('patient_name')} | UID: {cd.get('user_id')} | Email: {cd.get('email')}")

# 4. Check root 'cases'
root_case = db.collection("cases").document("OF-2026-6934").get()
print(f"4. Root 'cases/OF-2026-6934' exists: {root_case.exists}")
if root_case.exists:
    rc = root_case.to_dict()
    print(f"   UID: {rc.get('user_id')} | Email: {rc.get('email')} | Patient: {rc.get('patient_name')}")

# 5. Check backend get_user_analysis_history helper
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.firebase import get_user_analysis_history

history = get_user_analysis_history(ACTIVE_UID, USER_EMAIL)
print(f"5. Backend get_user_analysis_history returned: {len(history)} case(s)")
for h in history:
    print(f"   Case ID: {h.get('id') or h.get('case_id')} | Patient: {h.get('patient_name')}")

print("==================================================================")
if not old_doc.exists and len(active_subcases) >= 1 and root_case.to_dict().get('user_id') == ACTIVE_UID and len(history) >= 1:
    print("VERIFICATION RESULT: ALL CHECKS PASSED (UID Unified & Linked)")
else:
    print("VERIFICATION RESULT: SOME CHECKS FAILED")
print("==================================================================")
