import urllib.request
import urllib.parse
import urllib.error
import uuid
import json
from scratch.get_token import get_firebase_token

def test_large():
    token = get_firebase_token()
    if not token:
        print("Failed to get Firebase token.")
        return
        
    print("Got fresh token:", token[:30] + "...")
    
    # Generate 15MB of random bytes to simulate a large camera photo
    file_content = b'\x00' * (15 * 1024 * 1024)
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    filename = "large_test.jpg"
    
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
    
    try:
        with urllib.request.urlopen(req_upload) as r:
            res = json.loads(r.read().decode())
            print("LARGE UPLOAD STATUS:", r.status)
            print("LARGE UPLOAD RESPONSE:", res)
    except urllib.error.HTTPError as e:
        print("LARGE UPLOAD ERROR STATUS:", e.code)
        print("LARGE UPLOAD ERROR RESPONSE:", e.read().decode())

if __name__ == "__main__":
    test_large()
