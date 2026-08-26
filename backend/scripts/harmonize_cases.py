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


def harmonize_all_existing_cases():
    print("Harmonizing all existing cases across Firestore...")
    user_docs = list(db.collection("users").stream())
    total_synced = 0
    for udoc in user_docs:
        uid = udoc.id
        cases_stream = list(db.collection("users").document(uid).collection("cases").stream())
        for cdoc in cases_stream:
            data = cdoc.to_dict()
            case_id = cdoc.id
            raw_score = data.get("overall_score") or data.get("overallScore") or data.get("finishing_score") or data.get("abo_score") or 0
            score_int = int(round(float(raw_score))) if raw_score else 0

            updates = {
                "id": case_id,
                "case_id": case_id,
                "user_id": uid,
                "doctor_id": uid,
                "overall_score": score_int,
                "overall_finishing_score": score_int,
                "finishing_score": float(raw_score) if raw_score else float(score_int),
                "status": data.get("status") or "ANALYZED",
                "patient_name": data.get("patient_name") or data.get("patientName") or "Patient",
                "view_type": data.get("view_type") or data.get("viewType") or "opg",
                "image_url": data.get("image_url") or data.get("imagePath") or "",
            }

            # Merge update in user subcollection
            db.collection("users").document(uid).collection("cases").document(case_id).set(updates, merge=True)
            # Merge update in root collections
            db.collection("cases").document(case_id).set(dict(data, **updates), merge=True)
            db.collection("analysis_reports").document(case_id).set(dict(data, **updates), merge=True)
            db.collection("analyses").document(case_id).set(dict(data, **updates), merge=True)

            print(f"Synced case {case_id} for user {uid} (Score: {score_int}, Patient: {updates['patient_name']})")
            total_synced += 1

    print(f"\nSuccessfully harmonized {total_synced} cases across all collections.")


if __name__ == "__main__":
    harmonize_all_existing_cases()
