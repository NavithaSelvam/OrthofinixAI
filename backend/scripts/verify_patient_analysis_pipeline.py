import os
import sys
import json
import uuid
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

# Set paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db, save_analysis_record
from app.services.firebase_service import save_case_analysis
from app.db.sqlalchemy_db import get_db_session, SessionLocal
from app.db.orm_models import AnalysisReport, Patient as OrmPatient

print("==================================================")
print("TESTING END-TO-END PATIENT ANALYSIS PERSISTENCE")
print("==================================================")

init_firebase()
db = get_db()

test_uid = "doc_test_verification_user"
test_email = "doctor.test@orthofinix.com"
test_doctor_name = "Dr. Test Specialist"

test_patient_name = "Emma Watson"
test_dob = "2008-07-15"
test_gender = "Female"
test_case_id = f"case_test_{uuid.uuid4().hex[:8]}"

print(f"\n1. Simulating Case Analysis for Patient: {test_patient_name}")
print(f"   DOB: {test_dob}, Gender: {test_gender}, Case ID: {test_case_id}")

mock_metrics = {
    "andrews_details": [
        {"key": "molar_relationship", "score": 1.0, "explanation": "Class I relation"},
        {"key": "midline", "score": 1.0, "deviation_mm": 0.4}
    ],
    "overjet_overbite": {
        "overjet_mm": 2.5,
        "overbite_percent": 15.0
    },
    "segmented_teeth": {11: {}, 21: {}, 12: {}, 22: {}}
}

test_report_data = {
    "id": test_case_id,
    "case_id": test_case_id,
    "caseId": test_case_id,
    "patient_name": test_patient_name,
    "patientName": test_patient_name,
    "dob": test_dob,
    "gender": test_gender,
    "doctor_id": test_uid,
    "doctor_name": test_doctor_name,
    "doctor_email": test_email,
    "image_url": "https://orthofinixai-backend.onrender.com/uploads/sample_test.jpg",
    "view_type": "opg",
    "status": "completed",
    "finishing_score": 88.5,
    "alignment_score": 90.0,
    "confidence_score": 0.96,
    "midline_deviation_mm": 0.4,
    "overjet_mm": 2.5,
    "overbite_percent": 15.0,
    "abo_score": 88.0,
    "andrews_score": 89.0,
    "root_angulation_score": 87.5,
    "prediction": "Acceptable clinical orthodontic alignment achieved.",
    "recommendations": ["Minor tip adjustment FDI 12", "Proceed with standard retention"],
    "metrics": mock_metrics,
    "details": mock_metrics
}

# 2. Persist using save_case_analysis & save_analysis_record
save_case_analysis(test_uid, "sample_test.jpg", test_report_data)
save_analysis_record(
    test_report_data, 
    test_uid, 
    test_case_id, 
    user_email=test_email, 
    user_name=test_doctor_name,
    patient_dob=test_dob,
    patient_gender=test_gender
)

# 3. Persist to SQLite
session = SessionLocal()
try:
    sql_report = AnalysisReport(
        id=test_case_id,
        user_id=test_uid,
        case_id=test_case_id,
        patient_name=test_patient_name,
        image_url=test_report_data["image_url"],
        view_type="opg",
        status="completed",
        finishing_score=88.5,
        alignment_score=90.0,
        confidence_score=0.96,
        midline_deviation_mm=0.4,
        overjet_mm=2.5,
        overbite_percent=15.0,
        abo_score=88.0,
        andrews_score=89.0,
        root_angulation_score=87.5,
        prediction=test_report_data["prediction"],
        recommendations_json=json.dumps(test_report_data["recommendations"]),
        metrics_json=json.dumps(mock_metrics),
        created_at=datetime.now(timezone.utc)
    )
    session.merge(sql_report)
    session.commit()
    print("   Saved to SQLite database successfully.")
finally:
    session.close()

# 4. Verify Firestore Collections
print("\n2. Verifying Firestore Persistence across all collections...")

# Check cases/{case_id}
case_doc = db.collection("cases").document(test_case_id).get()
assert case_doc.exists, "FAILED: cases doc not found"
c_data = case_doc.to_dict()
print(f"   [cases/{test_case_id}]")
print(f"     patient_name: '{c_data.get('patient_name')}' | patientName: '{c_data.get('patientName')}'")
print(f"     score: {c_data.get('finishing_score')} | created_at: {c_data.get('created_at')}")
print(f"     patientProfile: {c_data.get('patientProfile', {}).get('name')}, DOB: {c_data.get('patientProfile', {}).get('dateOfBirth')}")
assert c_data.get("patient_name") == test_patient_name, "Patient name mismatch in cases"
assert c_data.get("patientName") == test_patient_name, "patientName mismatch in cases"

# Check patients
pat_docs = list(db.collection("patients").where("doctor_id", "==", test_uid).stream())
assert len(pat_docs) > 0, "FAILED: patient doc not found for doctor"
p_data = pat_docs[0].to_dict()
print(f"   [patients/{pat_docs[0].id}]")
print(f"     name: '{p_data.get('name')}' | DOB: '{p_data.get('date_of_birth')}' | Gender: '{p_data.get('gender')}' | Score: {p_data.get('last_score')}")
assert p_data.get("name") == test_patient_name, "Patient name mismatch in patients"
assert p_data.get("date_of_birth") == test_dob, "Patient DOB mismatch in patients"
assert p_data.get("gender") == test_gender, "Patient gender mismatch in patients"

# Check analysis_reports
rep_doc = db.collection("analysis_reports").document(test_case_id).get()
assert rep_doc.exists, "FAILED: analysis_reports doc not found"
assert rep_doc.to_dict().get("patient_name") == test_patient_name

# Check analyses
an_doc = db.collection("analyses").document(test_case_id).get()
assert an_doc.exists, "FAILED: analyses doc not found"
assert an_doc.to_dict().get("patient_name") == test_patient_name

# Check user subcollection
user_case_doc = db.collection("users").document(test_uid).collection("cases").document(test_case_id).get()
assert user_case_doc.exists, "FAILED: user case subcollection doc not found"
assert user_case_doc.to_dict().get("patient_name") == test_patient_name

print("\n==================================================")
print("VERIFICATION COMPLETE: 100% PERFECT PATIENT SAVING!")
print("==================================================")
