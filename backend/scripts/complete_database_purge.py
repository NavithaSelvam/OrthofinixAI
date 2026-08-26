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
    print("Error: Could not locate credentials.")
    sys.exit(1)

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def purge_all_firestore():
    print("=== 1. Purging All Cases Subcollections under Users ===")
    user_docs = list(db.collection("users").stream())
    for udoc in user_docs:
        uid = udoc.id
        sub_cases = list(db.collection("users").document(uid).collection("cases").stream())
        print(f"User {uid}: deleting {len(sub_cases)} cases in subcollection...")
        for sc in sub_cases:
            sc.reference.delete()
        # Reset total_cases to 0
        db.collection("users").document(uid).update({
            "total_cases": 0,
            "last_case_id": firestore.DELETE_FIELD
        })

    print("\n=== 2. Purging Root Collections ===")
    root_colls = ["cases", "analysis_reports", "analyses", "patients", "images", "activity_logs", "login_logs"]
    for col_name in root_colls:
        docs = list(db.collection(col_name).stream())
        print(f"Deleting {len(docs)} documents from '{col_name}'...")
        for d in docs:
            d.reference.delete()

def purge_sqlite_dbs():
    print("\n=== 3. Purging Backend SQLite Databases ===")
    dbs = [
        os.path.join(os.path.dirname(__file__), "..", "orthofinix_summit.db"),
        os.path.join(os.path.dirname(__file__), "..", "orthofinix.db"),
    ]
    for db_path in dbs:
        if os.path.exists(db_path):
            print(f"Wiping {db_path}...")
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
            for table in tables:
                if table != "sqlite_sequence":
                    try:
                        cur.execute(f"DELETE FROM {table};")
                    except Exception:
                        pass
            conn.commit()
            conn.close()

if __name__ == "__main__":
    purge_all_firestore()
    purge_sqlite_dbs()
    print("\n=== COMPLETE DATABASE PURGE FINISHED SUCCESSFULLY ===")
