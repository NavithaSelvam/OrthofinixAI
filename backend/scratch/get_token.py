import urllib.request
import urllib.error
import json

API_KEY = "AIzaSyCxuGJI0BFylFMX6g3EvdPs9lK_6odFBOA"

def get_firebase_token():
    # Try signing in first
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    login_data = {
        "email": "test_agent@example.com",
        "password": "Password123!",
        "returnSecureToken": True
    }
    
    req = urllib.request.Request(
        login_url,
        data=json.dumps(login_data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode())
            print("LOGIN SUCCESS")
            return res["idToken"]
    except urllib.error.HTTPError as e:
        # If login fails, try registering
        print("LOGIN FAILED, trying registration...")
        register_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        req_reg = urllib.request.Request(
            register_url,
            data=json.dumps(login_data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req_reg) as r_reg:
                res_reg = json.loads(r_reg.read().decode())
                print("REGISTRATION SUCCESS")
                return res_reg["idToken"]
        except urllib.error.HTTPError as e_reg:
            print("REGISTRATION FAILED:", e_reg.read().decode())
            return None

if __name__ == "__main__":
    token = get_firebase_token()
    if token:
        print("TOKEN:", token)
