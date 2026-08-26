import os
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

def update_firestore_rules():
    cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json")
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/firebase"]
    credentials = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    token = credentials.token

    project_id = "orthofinixai"
    
    rules_content = """rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}"""

    # Create a release for firestore rules via Firebase Rules API
    url = f"https://firebaserules.googleapis.com/v1/projects/{project_id}/rulesets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "source": {
            "files": [
                {
                    "name": "firestore.rules",
                    "content": rules_content
                }
            ]
        }
    }
    
    resp = requests.post(url, headers=headers, json=body)
    print("Create ruleset response:", resp.status_code, resp.text)
    if resp.status_code == 200:
        ruleset_name = resp.json().get("name")
        print("Created ruleset:", ruleset_name)
        
        # Release the ruleset
        release_url = f"https://firebaserules.googleapis.com/v1/projects/{project_id}/releases/cloud.firestore"
        release_body = {
            "release": {
                "name": f"projects/{project_id}/releases/cloud.firestore",
                "rulesetName": ruleset_name
            }
        }
        rel_resp = requests.patch(release_url, headers=headers, json=release_body)
        print("Release response:", rel_resp.status_code, rel_resp.text)
        if rel_resp.status_code == 200:
            print("Successfully deployed open Firestore rules for seamless sync!")
        else:
            # Try PUT
            rel_resp = requests.put(release_url, headers=headers, json={"rulesetName": ruleset_name})
            print("PUT response:", rel_resp.status_code, rel_resp.text)

if __name__ == "__main__":
    update_firestore_rules()
