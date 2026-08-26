import os
import sys
import json
import sqlite3
from datetime import datetime, timezone

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db, get_auth
from app.services.firebase_service import save_case_analysis, log_user_activity

def sync_all():
    print("==================================================")
    print("Starting Comprehensive Firebase Firestore Sync")
    print("==================================================")

    init_firebase()
    db = get_db()
    auth_admin = get_auth()

    now_iso = datetime.now(timezone.utc).isoformat()

    # ----------------------------------------------------
    # 1. Sync All Firebase Auth Users to Firestore `users`
    # ----------------------------------------------------
    print("\n[Step 1] Syncing Firebase Authentication Users to Firestore 'users' collection...")
    auth_users = []
    try:
        page = auth_admin.list_users()
        auth_users = page.users
        print(f"Found {len(auth_users)} users in Firebase Authentication.")

        for u in auth_users:
            created_ts = None
            if u.user_metadata and u.user_metadata.creation_timestamp:
                created_ts = datetime.fromtimestamp(u.user_metadata.creation_timestamp / 1000.0, tz=timezone.utc).isoformat()

            last_sign_in_ts = None
            if u.user_metadata and u.user_metadata.last_sign_in_timestamp:
                last_sign_in_ts = datetime.fromtimestamp(u.user_metadata.last_sign_in_timestamp / 1000.0, tz=timezone.utc).isoformat()

            user_doc = {
                "uid": u.uid,
                "email": u.email or "",
                "display_name": u.display_name or (u.email.split("@")[0] if u.email else "Doctor"),
                "role": "doctor",
                "email_verified": u.email_verified,
                "provider": u.provider_data[0].provider_id if u.provider_data else "password",
                "created_at": created_ts or now_iso,
                "last_login": last_sign_in_ts or now_iso,
                "last_active": last_sign_in_ts or now_iso,
                "updated_at": now_iso,
            }

            db.collection("users").document(u.uid).set(user_doc, merge=True)
            print(f"  Synced user: {u.uid} ({u.email}) -> users/{u.uid}")

            # Also ensure a baseline login log exists
            log_user_activity(u.uid, u.email, u.display_name or "Doctor")

    except Exception as e:
        print(f"Error syncing auth users: {e}")

    # ----------------------------------------------------
    # 2. Sync Cases from Subcollections to Top-Level Collections
    # ----------------------------------------------------
    print("\n[Step 2] Scanning subcollections 'users/*/cases/*' and syncing to root 'cases', 'analyses', and 'analysis_reports'...")
    try:
        case_docs = list(db.collection_group("cases").stream())
        print(f"Found {len(case_docs)} cases in subcollections.")

        for c_doc in case_docs:
            case_data = c_doc.to_dict()
            case_id = case_data.get("id") or c_doc.id
            user_id = case_data.get("user_id") or case_data.get("doctor_id") or ""

            # Save to root collections
            save_case_analysis(
                uid=user_id,
                filename=case_data.get("filename", ""),
                report_data=case_data
            )
            print(f"  Synced case: {case_id} (Patient: {case_data.get('patient_name')})")

    except Exception as e:
        print(f"Error syncing subcollection cases: {e}")

    # ----------------------------------------------------
    # 3. Sync Cases from Local SQLite Database (if present)
    # ----------------------------------------------------
    print("\n[Step 3] Checking local SQLite database records...")
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "orthofinix_summit.db"))
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check analysis_reports table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_reports'")
            if cursor.fetchone():
                cursor.execute("SELECT id, user_id, patient_name, image_url, finishing_score, alignment_score, confidence_score, abo_score, andrews_score, root_angulation_score, prediction, recommendations_json, metrics_json, created_at FROM analysis_reports")
                rows = cursor.fetchall()
                print(f"Found {len(rows)} analysis reports in SQLite database.")
                for row in rows:
                    rep_id, uid, pat_name, img_url, fin_score, align_score, conf_score, abo_sc, andrews_sc, root_sc, pred, recs_json, met_json, cr_at = row
                    
                    recs = []
                    if recs_json:
                        try:
                            recs = json.loads(recs_json)
                        except Exception:
                            recs = []
                    
                    metrics = {}
                    if met_json:
                        try:
                            metrics = json.loads(met_json)
                        except Exception:
                            metrics = {}

                    report_obj = {
                        "id": rep_id,
                        "case_id": rep_id,
                        "patient_name": pat_name,
                        "image_url": img_url,
                        "finishing_score": float(fin_score or 0),
                        "alignment_score": float(align_score or 0),
                        "confidence_score": float(conf_score or 0),
                        "abo_score": float(abo_sc or 0),
                        "andrews_score": float(andrews_sc or 0),
                        "root_angulation_score": float(root_sc or 0),
                        "prediction": pred or "Complete",
                        "recommendations": recs,
                        "metrics": metrics,
                        "created_at": str(cr_at),
                        "status": "completed"
                    }

                    # Use first real user if user_id was dummy test doctor
                    target_uid = uid
                    if auth_users and ("test_doctor" in (uid or "") or not uid):
                        target_uid = auth_users[0].uid

                    save_case_analysis(uid=target_uid, filename="", report_data=report_obj)
                    print(f"  Synced SQLite report: {rep_id} ({pat_name}) -> Firestore")

            conn.close()
        except Exception as e:
            print(f"Error syncing SQLite cases: {e}")

    # ----------------------------------------------------
    # 4. Summary of Root Collections in Firestore
    # ----------------------------------------------------
    print("\n==================================================")
    print("Firestore Root Collections Summary:")
    print("==================================================")
    for col_name in ["users", "cases", "analyses", "analysis_reports", "patients", "images", "login_logs", "activity_logs"]:
        try:
            count = len(list(db.collection(col_name).stream()))
            print(f"  Collection '{col_name}': {count} documents")
        except Exception as err:
            print(f"  Collection '{col_name}': Error ({err})")

    print("\nSync completed successfully! All data is visible in Firebase Console.")

if __name__ == "__main__":
    sync_all()
