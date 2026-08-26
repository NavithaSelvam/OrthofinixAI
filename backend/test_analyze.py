"""Quick test script for /analysis/analyze endpoint."""
import urllib.error
import urllib.request
import uuid


def test_form_urlencoded():
    data = b"upload_id=test123&patient_name=TestPatient&view_type=frontal"
    req = urllib.request.Request(
        "https://orthofinixai-backend.onrender.com/analysis/analyze",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            print("URLENCODED STATUS:", r.status)
            print(r.read().decode())
    except urllib.error.HTTPError as e:
        print("URLENCODED STATUS:", e.code)
        print(e.read().decode())


def test_multipart():
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    fields = [
        ("upload_id", "test123"),
        ("patient_name", "TestPatient"),
        ("view_type", "frontal"),
    ]
    body = ""
    for key, value in fields:
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
    body += f"--{boundary}--\r\n"
    req = urllib.request.Request(
        "https://orthofinixai-backend.onrender.com/analysis/analyze",
        data=body.encode(),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            print("MULTIPART STATUS:", r.status)
            print(r.read().decode())
    except urllib.error.HTTPError as e:
        print("MULTIPART STATUS:", e.code)
        print(e.read().decode())


if __name__ == "__main__":
    print("=== form-urlencoded ===")
    test_form_urlencoded()
    print("\n=== multipart ===")
    test_multipart()
