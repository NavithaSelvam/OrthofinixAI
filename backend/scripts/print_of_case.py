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

doc = db.collection("users").document("jcWf9mlE41d535G3X9Psyfb9mDT2").collection("cases").document("OF-2026-9963").get()
print("DOCUMENT EXISTS:", doc.exists)
if doc.exists:
    d = doc.to_dict()
    print("KEYS:", list(d.keys()))
    print("DOCTOR_ID / USER_ID:", d.get("user_id"), d.get("doctor_id"), d.get("doctorId"))
    print("PATIENT NAME:", d.get("patient_name"), d.get("patientName"))
    print("SCORES:", d.get("overall_score"), d.get("overallScore"), d.get("finishing_score"))
    print("ROOT cases/OF-2026-9963 EXISTS:", db.collection("cases").document("OF-2026-9963").get().exists)
    print("ROOT analysis_reports/OF-2026-9963 EXISTS:", db.collection("analysis_reports").document("OF-2026-9963").get().exists)
    print("ROOT analyses/OF-2026-9963 EXISTS:", db.collection("analyses").document("OF-2026-9963").get().exists)
