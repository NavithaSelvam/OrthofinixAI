import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.firebase_service import (
    init_firebase_admin,
    get_firestore_client,
    log_user_activity,
    save_case_analysis,
)

def test_firebase_firestore_pipeline():
    print("\n========================================================")
    print("Testing Firebase Firestore End-to-End Persistence Pipeline")
    print("========================================================")

    # 1. Initialize Firebase Admin
    init_firebase_admin()
    db = get_firestore_client()
    print("[1] Firebase Admin initialized successfully.")

    # 2. Test User Activity & Login Logging
    test_uid = f"test_doc_{uuid.uuid4().hex[:8]}"
    test_email = f"{test_uid}@orthofinix.ai"
    test_name = "Dr. Test Specialist"

    print(f"\n[2] Logging user activity for UID: {test_uid}...")
    user_res = log_user_activity(test_uid, test_email, test_name)
    assert user_res["uid"] == test_uid
    assert user_res["last_login"] is not None
    print(f"    User profile saved with last_login: {user_res['last_login']}")

    # Verify Firestore document exists in 'users'
    user_doc_ref = db.collection("users").document(test_uid).get()
    assert user_doc_ref.exists, f"User doc for {test_uid} was not found in Firestore!"
    user_doc = user_doc_ref.to_dict()
    print(f"    CONFIRMED Firestore doc: users/{test_uid}")
    print(f"    Doc details: email={user_doc.get('email')}, last_login={user_doc.get('last_login')}")

    # 3. Test Case Analysis Persistence
    test_case_id = f"case_test_{uuid.uuid4().hex[:8]}"
    test_filename = "opg_sample_01.jpg"
    test_report_data = {
        "id": test_case_id,
        "case_id": test_case_id,
        "patient_name": "Alexander Morgan",
        "finishing_score": 88.5,
        "abo_score": 84.0,
        "andrews_score": 89.0,
        "root_angulation_score": 85.5,
        "alignment_score": 90.0,
        "confidence_score": 0.95,
        "prediction": "Class I Molar with minor upper incisor rotation.",
        "recommendations": [
            "Upright tooth 33 by 3 degrees.",
            "Torque correction on tooth 11.",
            "Retain current arch width."
        ],
        "metrics": {
            "overjet_mm": 2.2,
            "overbite_percent": 25.0,
            "midline_deviation_mm": 0.4
        },
        "image_url": "https://orthofinixai.web.app/samples/sample_opg.jpg",
        "view_type": "opg"
    }

    print(f"\n[3] Saving Case Analysis for Case ID: {test_case_id}...")
    save_res = save_case_analysis(
        uid=test_uid,
        filename=test_filename,
        report_data=test_report_data
    )
    assert save_res["id"] == test_case_id
    print(f"    Case analysis successfully processed.")

    # 4. Verify Firestore collections
    print("\n[4] Verifying Documents Across Firestore Root Collections:")

    # Verify in 'analyses'
    analyses_doc = db.collection("analyses").document(test_case_id).get()
    assert analyses_doc.exists, f"Case {test_case_id} not found in 'analyses' collection!"
    print(f"    CONFIRMED: analyses/{test_case_id} (ABO Score: {analyses_doc.to_dict().get('abo_score')})")

    # Verify in 'cases'
    cases_doc = db.collection("cases").document(test_case_id).get()
    assert cases_doc.exists, f"Case {test_case_id} not found in 'cases' collection!"
    print(f"    CONFIRMED: cases/{test_case_id} (Finishing Score: {cases_doc.to_dict().get('finishing_score')})")

    # Verify in 'analysis_reports'
    reports_doc = db.collection("analysis_reports").document(test_case_id).get()
    assert reports_doc.exists, f"Case {test_case_id} not found in 'analysis_reports' collection!"
    print(f"    CONFIRMED: analysis_reports/{test_case_id} (Patient: {reports_doc.to_dict().get('patient_name')})")

    # Verify in user subcollection
    user_case_doc = db.collection("users").document(test_uid).collection("cases").document(test_case_id).get()
    assert user_case_doc.exists, f"Case not found in users/{test_uid}/cases/{test_case_id}"
    print(f"    CONFIRMED: users/{test_uid}/cases/{test_case_id}")

    # Clean up test documents
    print("\n[5] Cleaning up test artifacts...")
    try:
        db.collection("users").document(test_uid).collection("cases").document(test_case_id).delete()
        db.collection("analyses").document(test_case_id).delete()
        db.collection("cases").document(test_case_id).delete()
        db.collection("analysis_reports").document(test_case_id).delete()
        db.collection("users").document(test_uid).delete()
        print("    Cleaned up test documents successfully.")
    except Exception as e:
        print(f"    Notice during cleanup: {e}")

    print("\n========================================================")
    print("ALL TESTS PASSED! Firebase Firestore Pipeline is 100% Operational.")
    print("========================================================\n")

if __name__ == "__main__":
    test_firebase_firestore_pipeline()
