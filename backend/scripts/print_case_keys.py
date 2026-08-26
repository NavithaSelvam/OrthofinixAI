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
doc = db.collection("cases").document("OF-2026-9963").get().to_dict()
print("Top-level keys of OF-2026-9963:")
if doc:
    for k, v in doc.items():
        if not isinstance(v, (dict, list)):
            print(f"  {k}: {v}")
        elif isinstance(v, list) and len(v) < 5:
            print(f"  {k}: {v}")
        elif isinstance(v, dict):
            print(f"  {k}: [dict with {len(v)} keys]")
else:
    print("Document not found!")
