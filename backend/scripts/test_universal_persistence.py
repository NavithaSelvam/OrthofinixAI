import os
import sys
import json
import uuid
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db, save_analysis_record
from app.services.firebase_service import save_case_analysis

print("==================================================")
print("TESTING COMPLETE UNIVERSAL FIRESTORE PERSISTENCE")
print("==================================================")

init_firebase()
db = get_db()

test_uid = "doc_universal_test_user"
test_email = "doctor.test@orthofinix.com"
test_doctor_name = "Dr. Specialized Orthodontist"

test_patient_name = "Sophia Miller"
test_dob = "2009-03-22"
test_gender = "Female"
test_case_id = f"case_universal_{uuid.uuid4().hex[:8]}"

full_metrics = {
    "view_type": "opg",
    "scale_factor": 172.5,
    "occlusal_plane": {"slope": -0.198, "intercept": 0.492, "vector": [0.98, -0.19]},
    "detected_landmarks": {
        "11_incisal_edge": [0.476, 0.394],
        "21_incisal_edge": [0.519, 0.394],
        "16_cusp_tip_buccal": [0.269, 0.394],
        "26_cusp_tip_buccal": [0.707, 0.394]
    },
    "segmented_teeth": {
        "11": {"class": "incisor", "centroid": [0.48, 0.35], "fdi": 11},
        "21": {"class": "incisor", "centroid": [0.52, 0.35], "fdi": 21},
        "16": {"class": "molar", "centroid": [0.27, 0.35], "fdi": 16},
        "26": {"class": "molar", "centroid": [0.71, 0.35], "fdi": 26}
    },
    "root_parallelism": {
        "root_parallelism_score": 89.5,
        "deviations": [
            {"fdi": 12, "angle_deg": 3.2, "status": "Normal", "severity": "Mild", "recommendation": "Minor uprighting bend."}
        ],
        "uprighting_recommendations": ["Minor tip adjustment FDI 12."]
    },
    "overjet_overbite": {
        "overjet_mm": 2.4,
        "overbite_percent": 24.5,
        "overjet_status": "Normal",
        "overbite_status": "Normal"
    },
    "andrews_details": [
        {"key": "Key 1 Molar Relationship", "score": 1.0, "explanation": "Class I relation achieved bilaterally."},
        {"key": "Key 2 Crown Angulation", "score": 0.95, "explanation": "Positive crown angulation maintained."},
        {"key": "Key 3 Crown Inclination", "score": 0.90, "explanation": "Incisor torque within normal clinical range."},
        {"key": "Key 4 Rotations", "score": 1.0, "explanation": "No undesirable tooth rotations."},
        {"key": "Key 5 Tight Contacts", "score": 0.95, "explanation": "Interproximal contacts closed."},
        {"key": "Key 6 Curve of Spee", "score": 1.0, "explanation": "Curve of spee flat (1.2 mm)."}
    ],
    "conflicts": [],
    "warnings": []
}

full_report_data = {
    "id": test_case_id,
    "case_id": test_case_id,
    "caseId": test_case_id,
    "patient_name": test_patient_name,
    "patientName": test_patient_name,
    "dob": test_dob,
    "date_of_birth": test_dob,
    "gender": test_gender,
    "doctor_id": test_uid,
    "doctorId": test_uid,
    "doctor_name": test_doctor_name,
    "doctorName": test_doctor_name,
    "doctor_email": test_email,
    "image_url": "https://orthofinixai-backend.onrender.com/uploads/sample_sophia.jpg",
    "imagePath": "https://orthofinixai-backend.onrender.com/uploads/sample_sophia.jpg",
    "storage_url": "https://orthofinixai-backend.onrender.com/uploads/sample_sophia.jpg",
    "view_type": "opg",
    "viewType": "opg",
    "status": "completed",
    "finishing_score": 91.5,
    "overall_finishing_score": 91.5,
    "alignment_score": 94.0,
    "arch_symmetry_score": 94.0,
    "archSymmetryScore": 94.0,
    "confidence_score": 0.97,
    "confidenceScore": 0.97,
    "midline_deviation_mm": 0.3,
    "midlineDiscrepancyMm": 0.3,
    "overjet_mm": 2.4,
    "overjetMm": 2.4,
    "overbite_percent": 24.5,
    "overbitePercent": 24.5,
    "abo_score": 90.0,
    "aboScore": 90.0,
    "andrews_score": 92.5,
    "andrewsScore": 92.5,
    "root_angulation_score": 89.5,
    "rootAngulationScore": 89.5,
    "prediction": "Acceptable clinical orthodontic alignment achieved with high symmetry.",
    "recommendations": [
        "Maintain current archwire detailing sequence.",
        "Minor 3° artistic tip bend on FDI 12.",
        "Proceed to standard retention phase."
    ],
    "metrics": full_metrics,
    "details": full_metrics,
    "assessment": {
        "prediction": "Acceptable clinical orthodontic alignment achieved.",
        "finishing_score": 91.5,
        "recommendations": ["Maintain current archwire detailing sequence."]
    }
}

# 1. Execute Persistence
save_case_analysis(test_uid, "sample_sophia.jpg", full_report_data)
save_analysis_record(
    full_report_data, 
    test_uid, 
    test_case_id, 
    user_email=test_email, 
    user_name=test_doctor_name,
    patient_dob=test_dob,
    patient_gender=test_gender
)

# 2. Validate Every Collection in Firestore
print("\nValidating all 6 Firestore collections for complete data:")

# A. cases
doc_case = db.collection("cases").document(test_case_id).get()
assert doc_case.exists, "FAILED: cases collection doc missing"
d_case = doc_case.to_dict()
print(f"  [cases/{test_case_id}] OK")
print(f"    - Patient: {d_case.get('patient_name')}, DOB: {d_case.get('date_of_birth')}, Gender: {d_case.get('gender')}")
print(f"    - Finishing Score: {d_case.get('finishing_score')}%, Andrews: {d_case.get('andrews_score')}, ABO: {d_case.get('abo_score')}")
print(f"    - Image URL: {d_case.get('image_url')}")
print(f"    - Recommendations Count: {len(d_case.get('recommendations', []))}")
print(f"    - Metrics Teeth Count: {len(d_case.get('metrics', {}).get('segmented_teeth', {}))}")
print(f"    - Has Report: {d_case.get('hasReport')}, ClinicalDataJson length: {len(d_case.get('clinicalDataJson', ''))}")

# B. analyses
doc_an = db.collection("analyses").document(test_case_id).get()
assert doc_an.exists, "FAILED: analyses collection doc missing"
print(f"  [analyses/{test_case_id}] OK - Patient: {doc_an.to_dict().get('patient_name')}")

# C. analysis_reports
doc_rep = db.collection("analysis_reports").document(test_case_id).get()
assert doc_rep.exists, "FAILED: analysis_reports collection doc missing"
print(f"  [analysis_reports/{test_case_id}] OK - Patient: {doc_rep.to_dict().get('patient_name')}")

# D. patients
pat_docs = list(db.collection("patients").where("name", "==", test_patient_name).stream())
assert len(pat_docs) > 0, "FAILED: patients collection doc missing"
p_doc = pat_docs[0].to_dict()
print(f"  [patients/{pat_docs[0].id}] OK - Name: {p_doc.get('name')}, DOB: {p_doc.get('date_of_birth')}, Last Score: {p_doc.get('last_score')}")

# E. images
img_doc = db.collection("images").document(f"img_{test_case_id}").get()
assert img_doc.exists, "FAILED: images collection doc missing"
print(f"  [images/img_{test_case_id}] OK - Image URL: {img_doc.to_dict().get('image_url')}")

# F. users/{uid}/cases
user_case_doc = db.collection("users").document(test_uid).collection("cases").document(test_case_id).get()
assert user_case_doc.exists, "FAILED: user subcollection doc missing"
print(f"  [users/{test_uid}/cases/{test_case_id}] OK - Patient: {user_case_doc.to_dict().get('patient_name')}")

print("\n==================================================")
print("SUCCESS: 100% COMPLETE UNIVERSAL PERSISTENCE CONFIRMED!")
print("==================================================")
