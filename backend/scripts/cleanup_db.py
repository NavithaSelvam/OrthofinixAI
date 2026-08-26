import os
import sys
import glob
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

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

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def clear_collection(col_ref, batch_size=100):
    deleted = 0
    docs = list(col_ref.limit(batch_size).stream())
    while docs:
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            deleted += 1
        batch.commit()
        docs = list(col_ref.limit(batch_size).stream())
    return deleted

def cleanup_database():
    print("Cleaning subcollections 'cases'...")
    for doc in db.collection_group("cases").stream():
        doc.reference.delete()

    collections = ['patients', 'cases', 'analysis_reports', 'analyses', 'images', 'activity_logs', 'login_logs']
    for col_name in collections:
        cnt = clear_collection(db.collection(col_name))
        print(f"Deleted {cnt} documents from {col_name}.")

    print("Database cleanup completed successfully.")

if __name__ == "__main__":
    cleanup_database()
