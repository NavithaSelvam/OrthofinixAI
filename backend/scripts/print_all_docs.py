import os
import sys
import json
import firebase_admin
from firebase_admin import auth, firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()
db = get_firestore_client()

print("ALL FIRESTORE DOCUMENTS:")
for col in ["users", "cases", "analysis_reports", "analyses", "patients", "images"]:
    docs = list(db.collection(col).stream())
    print(f"\nCollection '{col}': {len(docs)} docs")
    for d in docs:
        data = d.to_dict()
        print(f"  [{col}/{d.id}] -> keys: {list(data.keys())[:8]} | user_id: {data.get('user_id') or data.get('doctorId') or data.get('doctor_id')} | patient: {data.get('patient_name') or data.get('name')}")
        if col == "users":
            for sc in db.collection("users").document(d.id).collection("cases").stream():
                sc_data = sc.to_dict()
                print(f"    Subcollection [users/{d.id}/cases/{sc.id}] -> patient: {sc_data.get('patient_name')}, score: {sc_data.get('overall_score') or sc_data.get('overallScore')}")
