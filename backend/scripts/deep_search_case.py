import os
import sys
import json
import sqlite3
import firebase_admin
from firebase_admin import auth, firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.services.firebase_service import init_firebase_admin, get_firestore_client
init_firebase_admin()
db = get_firestore_client()

target = "OF-2026-9963"
print(f"Searching for {target} everywhere:")

# Check SQL
conn = sqlite3.connect(os.path.join(BASE_DIR, "orthofinix_summit.db"))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
for table in tables:
    try:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        matches = [r for r in rows if any(target in str(c) or "keerthi" in str(c).lower() for c in r)]
        if matches:
            print(f"SQL {table} matches ({len(matches)}): {matches}")
    except Exception as e:
        print(f"SQL {table} error: {e}")
conn.close()

# Check Firestore collections
for col in ["users", "cases", "analysis_reports", "analyses", "patients", "images"]:
    docs = list(db.collection(col).stream())
    print(f"Firestore '{col}' (total {len(docs)}):")
    for d in docs:
        if target in d.id or "keerthi" in str(d.to_dict()).lower():
            print(f"  MATCH: {col}/{d.id} -> {json.dumps(d.to_dict(), default=str)[:200]}")
            if col == "users":
                sub_cases = list(db.collection("users").document(d.id).collection("cases").stream())
                print(f"    Subcollection cases ({len(sub_cases)}): {[sc.id for sc in sub_cases]}")
