import urllib.request
import urllib.parse
import urllib.error
import uuid
import json
import os

from scratch.get_token import get_firebase_token

def test_pipeline():
    token = get_firebase_token()
    if not token:
        print("Failed to get Firebase token.")
        return
        
    print("Got fresh token:", token[:30] + "...")
    
    # Use real dental image from uploads/
    image_path = "uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg"
    if not os.path.exists(image_path):
        print("Real dental image not found at path:", image_path)
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
            print("UPLOAD RESPONSE:", res)
            upload_id = res.get("upload_id")
    except urllib.error.HTTPError as e:
        print("UPLOAD ERROR STATUS:", e.code)
        print("UPLOAD ERROR RESPONSE:", e.read().decode())
        return
        
    if not upload_id:
        print("No upload_id returned.")
        return
        
    # 2. Analyze
    payload = {
        "upload_id": upload_id,
        "patient_name": "Test Patient",
        "view_type": "opg"
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
            print("ANALYZE STATUS:", r.status)
            print("ANALYZE RESPONSE:", r.read().decode())
    except urllib.error.HTTPError as e:
        print("ANALYZE ERROR STATUS:", e.code)
        print("ANALYZE ERROR RESPONSE:", e.read().decode())

if __name__ == "__main__":
    test_pipeline()
