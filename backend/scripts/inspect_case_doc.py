import os
import sys
import json
import firebase_admin
from firebase_admin import credentials, firestore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db

init_firebase()
db = get_db()

doc = db.document("users/ArYEcygXQ8W9ZecRUQbfpqTDQK92/cases/case_1787283884517").get()
if doc.exists:
    print("Found Doc:")
    print(json.dumps(doc.to_dict(), indent=2, default=str))
else:
    print("Doc not found")
