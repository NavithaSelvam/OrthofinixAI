import os
import sys
import glob
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

# Locate Firebase service account key
possible_creds = [
    "firebase_service_account.json",
    "firebase-adminsdk.json",
    "firebase-adminsdk.json.json",
    os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"),
    os.path.join(os.path.dirname(__file__), "..", "firebase-adminsdk.json"),
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

print(f"Initializing Firebase with credentials from: {cred_path}")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def clear_collection(col_ref):
    deleted = 0
    try:
        docs = list(col_ref.stream())
        for doc in docs:
            try:
                doc.reference.delete()
                deleted += 1
            except Exception:
                pass
    except Exception as e:
        print(f"Notice: {e}")
    return deleted

def clear_all():
    print("==================================================")
    print("PURGING ALL EXISTING CLINICAL DATA IN FIRESTORE")
    print("==================================================")

    # 1. Delete all case subcollections across all users by iterating users directly
    print("\n1. Deleting all user case subcollections...")
    sub_count = 0
    try:
        users_stream = list(db.collection("users").stream())
        for u in users_stream:
            user_cases = list(db.collection("users").document(u.id).collection("cases").stream())
            for c in user_cases:
                c.reference.delete()
                sub_count += 1
    except Exception as e:
        print(f"   Notice clearing user cases: {e}")
    print(f"   Deleted {sub_count} case documents from user subcollections.")

    # 2. Delete top-level collections
    collections_to_clear = [
        "cases",
        "patients",
        "analysis_reports",
        "analyses",
        "images",
        "activity_logs",
        "login_logs"
    ]

    for col_name in collections_to_clear:
        print(f"\n2. Clearing top-level collection '{col_name}'...")
        count = clear_collection(db.collection(col_name))
        print(f"   Deleted {count} documents from '{col_name}'.")

    # 3. Clean user case counters in 'users' collection (preserving accounts)
    print("\n3. Resetting case counters in 'users' collection...")
    users_docs = list(db.collection("users").stream())
    user_reset_count = 0
    for u_doc in users_docs:
        try:
            db.collection("users").document(u_doc.id).update({
                "total_cases": 0,
                "last_analysis_at": firestore.DELETE_FIELD,
                "last_case_id": firestore.DELETE_FIELD
            })
            user_reset_count += 1
        except Exception:
            pass
    print(f"   Reset metadata for {user_reset_count} user profiles.")

    # 4. Clean local SQLite databases
    print("\n4. Cleaning local SQLite databases...")
    sqlite_dbs = [
        os.path.join(os.path.dirname(__file__), "..", "orthofinix_summit.db"),
        os.path.join(os.path.dirname(__file__), "..", "orthofinix.db"),
    ]
    for db_file in sqlite_dbs:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in cursor.fetchall()]
                for tbl in ["analysis_reports", "patients_orm", "cases_orm", "uploaded_images_orm", "document_store"]:
                    if tbl in tables:
                        cursor.execute(f"DELETE FROM {tbl}")
                conn.commit()
                conn.close()
                print(f"   Cleaned tables in SQLite database: {os.path.basename(db_file)}")
            except Exception as sql_err:
                print(f"   SQLite clean warning for {db_file}: {sql_err}")

    # 5. Clean local uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    if os.path.exists(uploads_dir):
        files = glob.glob(os.path.join(uploads_dir, "*"))
        cleaned_files = 0
        for f in files:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    cleaned_files += 1
                except Exception:
                    pass
        print(f"\n5. Cleaned {cleaned_files} cached local image files from '{uploads_dir}'.")

    print("\n==================================================")
    print("ALL FIREBASE FIRESTORE DATA & LOCAL CACHES PURGED!")
    print("Ready for fresh new patient case analyses.")
    print("==================================================")

if __name__ == "__main__":
    clear_all()
