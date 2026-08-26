import urllib.request
import urllib.parse
import urllib.error
import uuid
import json
import os
from scratch.get_token import get_firebase_token

def test_frontal():
    token = get_firebase_token()
    if not token:
        print("Failed to get Firebase token.")
        return
        
    print("Got fresh token:", token[:30] + "...")
    
    # Use real dental image
    image_path = "uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg"
    if not os.path.exists(image_path):
        print("Real dental image not found.")
        return
        
    with open(image_path, "rb") as f:
        file_content = f.read()
        
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    filename = "test.jpg"
    
    # Construct multipart body
    body = []
    body.append(f'--{boundary}'.encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    body.append(b'Content-Type: image/jpeg')
    body.append(b'')
    body.append(file_content)
    body.append(f'--{boundary}--'.encode())
    body.append(b'')
    
    data = b'\r\n'.join(body)
    
    req_upload = urllib.request.Request(
        "https://orthofinixai-backend.onrender.com/analysis/upload",
        data=data,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}"
        }
    )
    
    upload_id = None
    try:
        with urllib.request.urlopen(req_upload) as r:
            res = json.loads(r.read().decode())
            print("UPLOAD STATUS:", r.status)
            upload_id = res.get("upload_id")
    except urllib.error.HTTPError as e:
        print("UPLOAD ERROR STATUS:", e.code)
        return
        
    if not upload_id:
        return
        
    # Analyze with frontal
    payload = {
        "upload_id": upload_id,
        "patient_name": "Test Patient",
        "view_type": "frontal"
    }
    data_analyze = urllib.parse.urlencode(payload).encode('utf-8')
    
    req_analyze = urllib.request.Request(
        "https://orthofinixai-backend.onrender.com/analysis/analyze",
        data=data_analyze,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        }
    )
    
    try:
        with urllib.request.urlopen(req_analyze) as r:
            print("FRONTAL ANALYZE STATUS:", r.status)
            print("FRONTAL ANALYZE RESPONSE:", r.read().decode()[:200] + "...")
    except urllib.error.HTTPError as e:
        print("FRONTAL ANALYZE ERROR STATUS:", e.code)
        print("FRONTAL ANALYZE ERROR RESPONSE:", e.read().decode())

if __name__ == "__main__":
    test_frontal()
