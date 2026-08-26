import os
import sys
import json
import firebase_admin
from firebase_admin import credentials, firestore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db, save_analysis_record
from app.services.firebase_service import save_case_analysis

init_firebase()
db = get_db()

print("==================================================")
print("SYNCING ALL USER SUBCOLLECTION CASES TO ROOT COLLECTIONS")
print("==================================================")

sub_cases = list(db.collection_group("cases").stream())
print(f"Found {len(sub_cases)} case(s) in Firestore subcollections:")

for sc in sub_cases:
    data = sc.to_dict()
    case_id = data.get("id") or data.get("case_id") or sc.id
    user_id = data.get("user_id") or data.get("uid") or data.get("doctor_id") or ""
    patient_name = data.get("patient_name") or data.get("patientName") or "Patient"
    
    # Path extraction
    path_parts = sc.reference.path.split("/")
    if len(path_parts) >= 4 and path_parts[0] == "users" and path_parts[2] == "cases":
        user_id = path_parts[1]

    print(f"Syncing case '{case_id}' for patient '{patient_name}' (user: {user_id})...")
    
    # Write to all top-level collections
    save_case_analysis(
        uid=user_id,
        filename=data.get("filename", ""),
        report_data=data
    )
    save_analysis_record(
        data=data,
        user_id=user_id,
        provided_case_id=case_id,
        patient_dob=data.get("dob") or data.get("date_of_birth") or "",
        patient_gender=data.get("gender") or "Unknown",
        patient_id=data.get("patient_id") or ""
    )

print("\nVerifying synced collections:")
for col in ["cases", "patients", "analyses", "analysis_reports", "images"]:
    count = len(list(db.collection(col).stream()))
    print(f"  - Collection '{col}': {count} doc(s)")

print("\n==================================================")
print("SYNC COMPLETE! ALL ROOT COLLECTIONS POPULATED.")
print("==================================================")
