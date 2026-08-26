import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.firebase import init_firebase, get_db, get_auth

def sync_existing_auth_users():
    print(">>> Initializing Firebase Admin...")
    init_firebase()
    
    db = get_db()
    auth_service = get_auth()
    
    print(">>> Fetching all users from Firebase Authentication...")
    try:
        page = auth_service.list_users()
        total_synced = 0
        
        while page:
            for user in page.users:
                uid = user.uid
                email = user.email or ""
                display_name = user.display_name or (email.split("@")[0] if email else "Doctor")
                created_at = datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000, tz=timezone.utc).isoformat() if user.user_metadata.creation_timestamp else datetime.now(timezone.utc).isoformat()
                last_sign_in = datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000, tz=timezone.utc).isoformat() if user.user_metadata.last_sign_in_timestamp else None
                
                user_doc = {
                    "uid": uid,
                    "email": email,
                    "display_name": display_name,
                    "role": "doctor",
                    "created_at": created_at,
                    "last_sign_in": last_sign_in,
                    "last_active": datetime.now(timezone.utc).isoformat(),
                    "email_verified": user.email_verified,
                    "provider_ids": [p.provider_id for p in user.provider_data] if user.provider_data else ["password"]
                }
                
                # Write to users/{uid} document
                db.collection("users").document(uid).set(user_doc, merge=True)
                print(f"   [OK] Synced user to Firestore: uid={uid}, email={email}, name={display_name}")
                total_synced += 1
                
            page = page.get_next_page()
            
        print(f"\n Successfully populated {total_synced} user profile document(s) in Firestore 'users' collection!")
        
    except Exception as e:
        print(f"Error syncing users: {e}")

if __name__ == "__main__":
    sync_existing_auth_users()
