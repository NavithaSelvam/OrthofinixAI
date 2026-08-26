import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=== USERS & SUBCASES ===")
users = list(db.collection("users").stream())
for u in users:
    data = u.to_dict() or {}
    subcases = list(db.collection("users").document(u.id).collection("cases").stream())
    print(f"User UID: {u.id}, Email: {data.get('email')}, Name: {data.get('name') or data.get('display_name')}, total_cases: {data.get('total_cases')}, subcases_count: {len(subcases)}")
    for sc in subcases:
        sc_data = sc.to_dict() or {}
        print(f"   -> Subcase ID: {sc.id}, patient_name: {sc_data.get('patient_name')}, overall_score: {sc_data.get('overall_score') or sc_data.get('overallScore')}")

print("\n=== ROOT CASES ===")
root_cases = list(db.collection("cases").stream())
print(f"Root cases count: {len(root_cases)}")
for rc in root_cases:
    rc_data = rc.to_dict() or {}
    print(f"   -> Case ID: {rc.id}, doctor_id: {rc_data.get('doctor_id') or rc_data.get('user_id')}, patient_name: {rc_data.get('patient_name')}")

print("\n=== ANALYSIS REPORTS ===")
reports = list(db.collection("analysis_reports").stream())
print(f"Reports count: {len(reports)}")
for r in reports:
    r_data = r.to_dict() or {}
    print(f"   -> Report ID: {r.id}, user_id: {r_data.get('user_id') or r_data.get('doctor_id')}, patient_name: {r_data.get('patient_name')}")
