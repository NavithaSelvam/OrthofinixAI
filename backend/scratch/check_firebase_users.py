from firebase_admin import auth
from app.db.firebase import init_firebase

def check():
    init_firebase()
    page = auth.list_users()
    print("USERS IN FIREBASE:")
    while page:
        for user in page.users:
            print(f"UID: {user.uid}, Email: {user.email}, Created: {user.user_metadata.creation_timestamp}")
        page = page.get_next_page()

if __name__ == "__main__":
    check()
