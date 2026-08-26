import os
import sys
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

def sanitize_firestore():
    cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json")
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("Sanitizing all Firestore documents to ensure ISO string created_at and numeric scores...")

    collections_to_check = ["cases", "analysis_reports", "analyses"]
    
    for coll_name in collections_to_check:
        docs = db.collection(coll_name).get()
        print(f"Checking collection '{coll_name}': {len(docs)} documents")
        for doc in docs:
            data = doc.to_dict()
            updates = {}
            raw_created = data.get("created_at")
            if raw_created is not None and not isinstance(raw_created, str):
                if hasattr(raw_created, "isoformat"):
                    updates["created_at"] = raw_created.isoformat()
                elif isinstance(raw_created, (int, float)):
                    updates["created_at"] = datetime.fromtimestamp(raw_created / 1000 if raw_created > 1e11 else raw_created, tz=timezone.utc).isoformat()
            
            # Ensure overall_score is a valid float/int
            score = data.get("overall_score") or data.get("overallScore") or data.get("finishing_score") or data.get("overall_finishing_score")
            if score is not None:
                try:
                    f_score = float(score)
                    updates["overall_score"] = f_score
                    updates["overallScore"] = f_score
                    updates["finishing_score"] = f_score
                except Exception:
                    pass

            if updates:
                doc.reference.update(updates)
                print(f"  -> Updated {coll_name}/{doc.id}: {updates.keys()}")

    # Check user subcollections
    users = db.collection("users").get()
    print(f"Checking {len(users)} user collections...")
    for u in users:
        u_cases = u.reference.collection("cases").get()
        for doc in u_cases:
            data = doc.to_dict()
            updates = {}
            raw_created = data.get("created_at")
            if raw_created is not None and not isinstance(raw_created, str):
                if hasattr(raw_created, "isoformat"):
                    updates["created_at"] = raw_created.isoformat()
                elif isinstance(raw_created, (int, float)):
                    updates["created_at"] = datetime.fromtimestamp(raw_created / 1000 if raw_created > 1e11 else raw_created, tz=timezone.utc).isoformat()
            
            score = data.get("overall_score") or data.get("overallScore") or data.get("finishing_score") or data.get("overall_finishing_score")
            if score is not None:
                try:
                    f_score = float(score)
                    updates["overall_score"] = f_score
                    updates["overallScore"] = f_score
                    updates["finishing_score"] = f_score
                except Exception:
                    pass

            if updates:
                doc.reference.update(updates)
                print(f"  -> Updated users/{u.id}/cases/{doc.id}: {updates.keys()}")

    print("Sanitization complete!")

if __name__ == "__main__":
    sanitize_firestore()
