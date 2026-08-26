import os
import sys
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

possible_creds = [
    "firebase_service_account.json",
    "firebase-adminsdk.json",
    "firebase-adminsdk.json.json",
    os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"),
    os.path.join(os.path.dirname(__file__), "..", "firebase-adminsdk.json"),
    os.path.join(os.path.dirname(__file__), "..", "firebase-adminsdk.json.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "firebase_service_account.json"),
]

cred_path = None
for p in possible_creds:
    if os.path.exists(p):
        cred_path = p
        break

if not cred_path:
    print("Error: Could not locate firebase_service_account.json credentials file.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

SYNTHETIC_PATTERNS = [
    "doctor_alpha",
    "doctor_beta",
    "dr_prod_user",
    "doc_test",
    "test_doc",
    "doctor_uid",
    "test_user",
    "user_a",
    "user_b",
    "test_case",
    "synthetic",
    "mock_",
    "CASE_ANDROID_",
    "CASE_WEB_",
    "CASE_USER_",
    "demo-summit-case",
]

def is_synthetic(val: str) -> bool:
    if not val:
        return False
    val_lower = str(val).lower()
    return any(p.lower() in val_lower for p in SYNTHETIC_PATTERNS)

def purge_synthetic_firestore():
    print("=== Purging Synthetic Test Documents from Firestore ===")
    
    # 1. Check users collection
    purged_user_ids = set()
    user_docs = list(db.collection("users").stream())
    for doc in user_docs:
        d = doc.to_dict()
        uid = doc.id
        email = d.get("email", "")
        name = d.get("display_name", "")
        if is_synthetic(uid) or is_synthetic(email) or is_synthetic(name):
            print(f"Purging synthetic user: {uid} ({email})")
            # Delete user's subcollections
            for subdoc in db.collection("users").document(uid).collection("cases").stream():
                subdoc.reference.delete()
            doc.reference.delete()
            purged_user_ids.add(uid)

    # 2. Check collection group 'cases'
    for doc in db.collection_group("cases").stream():
        d = doc.to_dict()
        cid = doc.id
        uid = d.get("user_id", "") or d.get("doctor_id", "")
        pname = d.get("patient_name", "") or d.get("patientName", "")
        if cid in purged_user_ids or uid in purged_user_ids or is_synthetic(cid) or is_synthetic(uid) or is_synthetic(pname):
            print(f"Purging subcollection case: {cid} (Patient: {pname}, User: {uid})")
            doc.reference.delete()

    # 3. Check root collections
    root_colls = ["cases", "analysis_reports", "analyses", "patients", "images", "activity_logs", "login_logs"]
    for col_name in root_colls:
        col_docs = list(db.collection(col_name).stream())
        deleted_count = 0
        for doc in col_docs:
            d = doc.to_dict()
            doc_id = doc.id
            uid = d.get("user_id", "") or d.get("doctor_id", "") or d.get("doctorId", "") or d.get("uid", "")
            pname = d.get("patient_name", "") or d.get("patientName", "") or d.get("name", "")
            email = d.get("email", "") or d.get("doctor_email", "")

            if (doc_id in purged_user_ids or 
                uid in purged_user_ids or 
                is_synthetic(doc_id) or 
                is_synthetic(uid) or 
                is_synthetic(pname) or 
                is_synthetic(email)):
                doc.reference.delete()
                deleted_count += 1

        print(f"Cleaned {deleted_count} synthetic documents from '{col_name}'.")

def purge_synthetic_sqlite():
    print("\n=== Purging Synthetic Records from SQLite Databases ===")
    db_paths = [
        os.path.join(os.path.dirname(__file__), "..", "orthofinix_summit.db"),
        os.path.join(os.path.dirname(__file__), "..", "orthofinix.db"),
    ]
    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
        print(f"Cleaning database: {db_path}")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        
        for table in tables:
            cols = [c[1] for c in cur.execute(f"PRAGMA table_info({table});").fetchall()]
            for pattern in SYNTHETIC_PATTERNS:
                like_expr = f"%{pattern}%"
                for col in ["id", "user_id", "doctor_id", "email", "patient_name", "name"]:
                    if col in cols:
                        try:
                            cur.execute(f"DELETE FROM {table} WHERE {col} LIKE ?", (like_expr,))
                        except Exception:
                            pass
        conn.commit()
        conn.close()
        print(f"Database {db_path} cleaned successfully.")

if __name__ == "__main__":
    purge_synthetic_firestore()
    purge_synthetic_sqlite()
    print("\n=== All Synthetic Test Data Purged Successfully ===")
