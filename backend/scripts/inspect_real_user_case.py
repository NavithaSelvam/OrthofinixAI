import os
import sys
import json
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import auth, firestore, storage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()


def inspect_all_real_cases():
    db = get_firestore_client()
    print("=" * 80)
    print("INSPECTING CLOUD FIRESTORE FOR REAL USER CASES...")
    print("=" * 80)

    # 1. Inspect Firebase Auth users
    print("\n--- 1. FIREBASE AUTHENTICATION USERS ---")
    users = list(auth.list_users().iterate_all())
    user_map = {}
    for u in users:
        print(f"User: UID={u.uid}, Email={u.email}, DisplayName={u.display_name}, Created={u.user_metadata.creation_timestamp}")
        user_map[u.uid] = u

    # 2. Inspect users collection and subcollections
    print("\n--- 2. FIRESTORE users/{uid}/cases ---")
    user_cases_found = []
    user_docs = db.collection("users").stream()
    for udoc in user_docs:
        uid = udoc.id
        u_data = udoc.to_dict()
        print(f"\nUser Doc: {uid} -> {u_data.get('email', 'No email')} (total_cases: {u_data.get('total_cases')})")
        cases_stream = db.collection("users").document(uid).collection("cases").stream()
        for cdoc in cases_stream:
            cdata = cdoc.to_dict()
            user_cases_found.append({
                "source": f"users/{uid}/cases/{cdoc.id}",
                "doc_id": cdoc.id,
                "user_id": uid,
                "data": cdata
            })
            print(f"  -> Case: {cdoc.id}")
            print(f"     Patient: {cdata.get('patient_name') or cdata.get('patientName')}")
            print(f"     Overall Score: {cdata.get('overall_score') or cdata.get('overallScore') or cdata.get('finishing_score')}")
            print(f"     ABO Score: {cdata.get('abo_score') or cdata.get('aboScore')}")
            print(f"     Andrews Score: {cdata.get('andrews_score') or cdata.get('andrewsScore')}")
            print(f"     Confidence: {cdata.get('confidence_score') or cdata.get('confidenceScore')}")
            print(f"     Image URL: {cdata.get('image_url') or cdata.get('imagePath')}")
            print(f"     Created At: {cdata.get('created_at') or cdata.get('createdAt')}")
            print(f"     Status: {cdata.get('status')}")

    # 3. Inspect top-level 'cases' collection
    print("\n--- 3. FIRESTORE root 'cases' collection ---")
    root_cases = list(db.collection("cases").stream())
    print(f"Total root cases: {len(root_cases)}")
    for rc in root_cases:
        rdata = rc.to_dict()
        print(f"  -> Case: {rc.id} | User: {rdata.get('user_id') or rdata.get('doctor_id')} | Patient: {rdata.get('patient_name') or rdata.get('patientName')} | Score: {rdata.get('overall_score') or rdata.get('overallScore')}")

    # 4. Inspect top-level 'analysis_reports' collection
    print("\n--- 4. FIRESTORE root 'analysis_reports' collection ---")
    root_reports = list(db.collection("analysis_reports").stream())
    print(f"Total root analysis_reports: {len(root_reports)}")
    for rr in root_reports:
        rrdata = rr.to_dict()
        print(f"  -> Report: {rr.id} | User: {rrdata.get('user_id') or rrdata.get('doctor_id')} | Patient: {rrdata.get('patient_name')} | Score: {rrdata.get('overall_score') or rrdata.get('finishing_score')}")

    # 5. Inspect top-level 'analyses' collection
    print("\n--- 5. FIRESTORE root 'analyses' collection ---")
    root_analyses = list(db.collection("analyses").stream())
    print(f"Total root analyses: {len(root_analyses)}")
    for ra in root_analyses:
        radata = ra.to_dict()
        print(f"  -> Analysis: {ra.id} | User: {radata.get('user_id') or radata.get('doctor_id')} | Patient: {radata.get('patient_name') or radata.get('patientName')}")

    # 6. Check SQL Database
    print("\n--- 6. SQL DATABASE RECORDS ---")
    from app.db.sqlalchemy_db import get_db_context
    from app.db.orm_models import AnalysisReport, Case, Patient
    with get_db_context() as session:
        reports = session.query(AnalysisReport).order_by(AnalysisReport.created_at.desc()).limit(10).all()
        print(f"Total SQL AnalysisReports: {len(reports)}")
        for rep in reports:
            print(f"  -> SQL Report: {rep.id} | User: {rep.user_id} | Patient: {rep.patient_name} | Score: {rep.finishing_score} | Created: {rep.created_at}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    inspect_all_real_cases()
