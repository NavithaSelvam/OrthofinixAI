import os
import sys
import firebase_admin
from firebase_admin import credentials, auth, firestore
from sqlalchemy.orm import Session

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.sqlalchemy_db import SessionLocal
from app.db.orm_models import AnalysisReport, Case, Patient, UploadedImage

cred_path = "backend/firebase-adminsdk.json"
if not os.path.exists(cred_path):
    cred_path = "firebase-adminsdk.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("ORTHOFINIX AI: COMPLETE SYSTEM & AUTH PURGE (100% CLEAN SLATE)")
print("=" * 80)

# 1. Purge ALL users from Firebase Authentication
print("\n[1] Deleting ALL users from Firebase Authentication...")
page = auth.list_users()
deleted_auth_count = 0
while page:
    for u in page.users:
        try:
            auth.delete_user(u.uid)
            deleted_auth_count += 1
            print(f" -> Deleted Auth User: {u.uid} ({u.email})")
        except Exception as e:
            print(f" -> Error deleting Auth user {u.uid}: {e}")
    page = page.get_next_page()
print(f"Total Firebase Auth Users Deleted: {deleted_auth_count}")

# 2. Recursively delete all documents and subcollections across Firestore
all_colls = [
    "users",
    "cases",
    "analyses",
    "analysis_reports",
    "patients",
    "images",
    "activity_logs",
    "login_logs"
]

def recursively_delete_doc(doc_ref):
    try:
        for sub_col in doc_ref.collections():
            for sub_doc in sub_col.stream():
                recursively_delete_doc(sub_doc.reference)
        doc_ref.delete()
    except Exception as e:
        print(f"Error recursively deleting {doc_ref.path}: {e}")

print("\n[2] Wiping all Firestore collections and subcollections...")
for coll_name in all_colls:
    docs = list(db.collection(coll_name).stream())
    print(f" -> Wiping '{coll_name}' ({len(docs)} documents)...")
    for doc in docs:
        recursively_delete_doc(doc.reference)
    print(f" -> Collection '{coll_name}' wiped cleanly.")

# 3. Clear local SQL database tables
print("\n[3] Clearing local/cloud SQL database tables...")
session: Session = SessionLocal()
try:
    session.query(AnalysisReport).delete()
    session.query(Case).delete()
    session.query(Patient).delete()
    session.query(UploadedImage).delete()
    session.commit()
    print(" -> SQL Database wiped cleanly.")
except Exception as e:
    session.rollback()
    print(f" -> SQL Database wipe notice: {e}")
finally:
    session.close()

print("\n" + "=" * 80)
print("100% CLEAN SLATE SYSTEM PURGE COMPLETE!")
print("=" * 80)
