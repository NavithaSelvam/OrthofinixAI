from app.db.firebase import init_firebase, get_db
from datetime import datetime, timezone
import os

def check():
    init_firebase()
    db = get_db()
    
    # Let's list cases from all users
    # Since we use collection_group("cases"), we can query all cases across all users!
    docs = db.collection_group("cases").order_by("created_at").limit(10).stream()
    
    print("REPORTS IN FIRESTORE:")
    for doc in docs:
        d = doc.to_dict()
        print(f"ID: {d.get('id')}, Patient: {d.get('patient_name')}, Time: {d.get('created_at')}, Status: {d.get('status')}")

if __name__ == "__main__":
    check()
