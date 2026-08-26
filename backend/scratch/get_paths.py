import urllib.request
import json

url = "https://orthofinixai-backend.onrender.com/openapi.json"
try:
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read().decode())
        print("PATHS:")
        for path, methods in data["paths"].items():
            print(f"  {path} -> {list(methods.keys())}")
except Exception as e:
    print("ERROR:", e)
