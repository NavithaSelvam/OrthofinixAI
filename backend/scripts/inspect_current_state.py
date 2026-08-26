import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

possible_creds = [
    "firebase_service_account.json",
    "firebase-adminsdk.json",
    "firebase-adminsdk.json.json",
    os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"),
    os.path.join(os.path.dirname(__file__), "..", "firebase-adminsdk.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "firebase_service_account.json"),
]

cred_path = None
for p in possible_creds:
    if os.path.exists(p):
        cred_path = p
        break

if not cred_path:
    print("Error: Could not locate credentials.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("\n--- ALL USERS IN FIRESTORE ---")
for doc in db.collection("users").stream():
    d = doc.to_dict()
    print(f"User ID: {doc.id} | Email: {d.get('email')} | Display Name: {d.get('display_name')} | Total Cases: {d.get('total_cases')}")
    # check subcollection cases
    sub_cases = list(db.collection("users").document(doc.id).collection("cases").stream())
    print(f"  -> Subcollection 'cases' count: {len(sub_cases)}")
    for sc in sub_cases:
        scd = sc.to_dict()
        print(f"     Case ID: {sc.id} | Patient: {scd.get('patient_name') or scd.get('patientName')} | Score: {scd.get('finishing_score') or scd.get('overall_score')}")

print("\n--- ALL CASES IN TOP-LEVEL 'cases' ---")
for doc in db.collection("cases").stream():
    d = doc.to_dict()
    print(f"Case ID: {doc.id} | User ID: {d.get('user_id') or d.get('doctor_id')} | Patient: {d.get('patient_name') or d.get('patientName')}")

print("\n--- ALL IN 'analysis_reports' ---")
for doc in db.collection("analysis_reports").stream():
    d = doc.to_dict()
    print(f"Report ID: {doc.id} | User ID: {d.get('user_id') or d.get('doctor_id')} | Patient: {d.get('patient_name') or d.get('patientName')}")
