import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
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
print("STARTING FRESH: COMPLETE DATABASE & ANALYSIS RECORDS WIPE")
print("=" * 80)

# 1. Clear SQLite Database Tables
print("\n[1] Clearing local/cloud SQL database tables...")
session: Session = SessionLocal()
try:
    num_reports = session.query(AnalysisReport).delete()
    num_cases = session.query(Case).delete()
    num_patients = session.query(Patient).delete()
    num_images = session.query(UploadedImage).delete()
    session.commit()
    print(f" -> SQL Purge: Deleted {num_reports} reports, {num_cases} cases, {num_patients} patients, {num_images} images.")
except Exception as e:
    session.rollback()
    print(f" -> SQL Purge Notice: {e}")
finally:
    session.close()

# 2. Clear Root Firestore Collections
root_colls = ["cases", "analyses", "analysis_reports", "patients", "images"]
for coll_name in root_colls:
    print(f"\n[2] Wiping Firestore root collection '{coll_name}'...")
    docs = list(db.collection(coll_name).stream())
    for doc in docs:
        try:
            doc.reference.delete()
        except Exception as e:
            print(f"Error deleting {coll_name}/{doc.id}: {e}")
    print(f" -> Wiped {len(docs)} documents from '{coll_name}'.")

# 3. Clear User Subcollections & Reset total_cases
print("\n[3] Wiping all user subcollections ('cases' and 'analyses') and resetting total_cases...")
user_docs = list(db.collection("users").stream())
for u_doc in user_docs:
    uid = u_doc.id
    # Clear users/{uid}/cases
    user_cases = list(u_doc.reference.collection("cases").stream())
    for c_doc in user_cases:
        c_doc.reference.delete()
    
    # Clear users/{uid}/analyses
    user_analyses = list(u_doc.reference.collection("analyses").stream())
    for a_doc in user_analyses:
        a_doc.reference.delete()
        
    u_doc.reference.set({"total_cases": 0}, merge=True)
    print(f" -> Reset users/{uid}: Wiped {len(user_cases)} cases & {len(user_analyses)} analyses.")

print("\n" + "=" * 80)
print("FRESH DATABASE INITIALIZATION COMPLETE — ALL OLD CASES PURGED!")
print("=" * 80)
