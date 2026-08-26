import urllib.request
import urllib.parse
import urllib.error
import json
import sys

TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3YzQ1NTQ4NTU1NTYxOTYwZjQ5MWQ1MDYzOWU1NTY1N2IyMTJhYmMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vb3J0aG9maW5peGFpIiwiYXVkIjoib3J0aG9maW5peGFpIiwiYXV0aF90aW1lIjoxNzg2NTI0MDk1LCJ1c2VyX2lkIjoiNndqc244TUIyNVB2RGRhdlJlTW1xdEZnVUE5MiIsInN1YiI6IjZ3anNuOE1CMjVQdkRkYXZSZU1tcXRGZ1VBOTIiLCJpYXQiOjE3ODY1MjQwOTUsImV4cCI6MTc4NjUyNzY5NSwiZW1haWwiOiJ0ZXN0X2FnZW50QGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbInRlc3RfYWdlbnRAZXhhbXBsZS5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.VFxq7zWtqXMZvmTffvmg9bjyJtRDOg5loy_SaocjkT7UQPEi9kmg0_nKnYXsHnt6TWQ6xYEaqFpAEm86bNQuMtOfEpCJ9wTuFM8VJX6ECn5F86fNQ0rk3qCAu1-2PzOf6pGAACdNPOJaJJBNoBsCtHnf83xpW6pofNXWArMW0XT1D3c2sv7lgTnw5oHBfmLHkK8cslSa_ruz-G0FzBfVQGFprRD6dLnx8eBz6m0XXVxtS4YSw5uCgESUNr4bP32SXFamq7w7Nh6jlJNHePOzpa8o_Cty8H8A2u5yR0Y9OWqdYt7t-utyzgumNMrMkMYVg7sZpGfvj-d6xgehXpJ_gw"

def analyze_image(upload_id):
    payload = {
        "upload_id": upload_id,
        "patient_name": "Test Patient",
        "view_type": "frontal"
    }
    data = urllib.parse.urlencode(payload).encode('utf-8')
    
    req = urllib.request.Request(
        "https://orthofinixai-backend.onrender.com/analysis/analyze",
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {TOKEN}"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as r:
            print("STATUS:", r.status)
            print("RESPONSE:", r.read().decode())
    except urllib.error.HTTPError as e:
        print("ERROR STATUS:", e.code)
        print("ERROR RESPONSE:", e.read().decode())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide upload_id")
        sys.exit(1)
    analyze_image(sys.argv[1])
