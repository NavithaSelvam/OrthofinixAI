import os
import sys
import json
import firebase_admin
from firebase_admin import auth, firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()


def inspect_keerthi_case():
    case_id = "OF-2026-9963"
    db = get_firestore_client()
    print("=" * 80)
    print(f"INSPECTING EXACT USER CASE: {case_id}")
    print("=" * 80)

    # Check root cases
    rc = db.collection("cases").document(case_id).get()
    print(f"1. root 'cases/{case_id}' exists: {rc.exists}")
    if rc.exists:
        print(f"   Data: {json.dumps(rc.to_dict(), default=str, indent=2)}")

    # Check root analysis_reports
    rr = db.collection("analysis_reports").document(case_id).get()
    print(f"\n2. root 'analysis_reports/{case_id}' exists: {rr.exists}")
    if rr.exists:
        print(f"   Data: {json.dumps(rr.to_dict(), default=str, indent=2)}")

    # Check users/{uid}/cases/{case_id}
    print("\n3. Scanning all user subcollections for this case:")
    for udoc in db.collection("users").stream():
        uid = udoc.id
        uc = db.collection("users").document(uid).collection("cases").document(case_id).get()
        if uc.exists:
            print(f"   -> FOUND in users/{uid}/cases/{case_id}!")
            print(f"      User doc email: {udoc.to_dict().get('email')}")
            print(f"      Data: {json.dumps(uc.to_dict(), default=str, indent=2)}")
        else:
            # Query if case_id or id matches in that user's subcollection
            q = list(db.collection("users").document(uid).collection("cases").where("case_id", "==", case_id).stream())
            if q:
                for match in q:
                    print(f"   -> MATCHED by query in users/{uid}/cases/{match.id}!")
                    print(f"      Data: {json.dumps(match.to_dict(), default=str, indent=2)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    inspect_keerthi_case()
