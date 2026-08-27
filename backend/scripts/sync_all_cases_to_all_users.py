import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.db.firebase import init_firebase, get_db

def sync_cases():
    init_firebase()
    db = get_db()
    
    users = [u.to_dict() for u in db.collection('users').stream()]
    print(f"Total Users Found in Firestore: {len(users)}")
    for u in users:
        print(f"  - User: {u.get('email')} (UID: {u.get('uid')})")
        
    root_cases = [c.to_dict() for c in db.collection('cases').stream()]
    print(f"\nTotal Root Cases Found: {len(root_cases)}")
    for c in root_cases:
        cid = c.get('id') or c.get('case_id')
        pname = c.get('patient_name') or c.get('patientName') or 'Patient'
        score = c.get('overall_score') or c.get('finishing_score') or 0
        print(f"  - Case: {cid} | Patient: {pname} | Score: {score}")

    for u in users:
        uid = u.get('uid')
        if not uid:
            continue
        email = u.get('email')
        for c in root_cases:
            cid = c.get('id') or c.get('case_id')
            if not cid:
                continue
            c_copy = dict(c)
            c_copy['doctor_id'] = uid
            c_copy['doctorId'] = uid
            c_copy['user_id'] = uid
            c_copy['userId'] = uid
            db.collection('users').document(uid).collection('cases').document(cid).set(c_copy, merge=True)
            print(f"Synced case {cid} to user {email}")

    print("\n[SUCCESS] All accounts are now fully synchronized with identical cases!")

if __name__ == '__main__':
    sync_cases()
