import firebase_admin
from firebase_admin import credentials, firestore
import os

cred_path = "backend/firebase-adminsdk.json"
if os.path.exists(cred_path):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()
uid = "YpC45yYkPmPioe69576OYnBGtHF3"

print("=" * 70)
print(f"INSPECTING FIRESTORE DOCUMENTS FOR USER UID: {uid}")
print("=" * 70)

# Check users/{uid}/cases
sub_cases = list(db.collection("users").document(uid).collection("cases").stream())
print(f"users/{uid}/cases count: {len(sub_cases)}")
for doc in sub_cases:
    d = doc.to_dict()
    print(f"  Doc ID: {doc.id} | patient_name: {d.get('patient_name')} | case_id: {d.get('case_id')} | id: {d.get('id')}")

# Check root 'cases'
root_cases = list(db.collection("cases").stream())
print(f"\nRoot 'cases' total count: {len(root_cases)}")
for doc in root_cases:
    d = doc.to_dict()
    if d.get("user_id") == uid or d.get("userId") == uid or d.get("doctor_id") == uid:
        print(f"  [Matches UID] Doc ID: {doc.id} | patient_name: {d.get('patient_name')} | case_id: {d.get('case_id')}")

# Check root 'analysis_reports'
reports = list(db.collection("analysis_reports").stream())
print(f"\nRoot 'analysis_reports' total count: {len(reports)}")
for doc in reports:
    d = doc.to_dict()
    if d.get("user_id") == uid or d.get("userId") == uid:
        print(f"  [Matches UID] Doc ID: {doc.id} | patient_name: {d.get('patient_name')}")

# Check root 'analyses'
analyses = list(db.collection("analyses").stream())
print(f"\nRoot 'analyses' total count: {len(analyses)}")
for doc in analyses:
    d = doc.to_dict()
    if d.get("user_id") == uid or d.get("userId") == uid:
        print(f"  [Matches UID] Doc ID: {doc.id} | patient_name: {d.get('patient_name')}")
