import requests

base_url = "https://orthofinixai-backend.onrender.com"
print("Pinging Render backend at:", base_url)

# 1. GET /
try:
    r1 = requests.get(f"{base_url}/", timeout=120)
    print(f"1. GET / -> Status: {r1.status_code}, Body: {r1.text.strip()}")
except Exception as e:
    print(f"1. GET / -> Error: {e}")

# 2. GET /docs
try:
    r2 = requests.get(f"{base_url}/docs", timeout=120)
    print(f"2. GET /docs -> Status: {r2.status_code}, Length: {len(r2.text)} bytes")
except Exception as e:
    print(f"2. GET /docs -> Error: {e}")

# 3. GET /analysis/history without token
try:
    r3 = requests.get(f"{base_url}/analysis/history", timeout=120)
    print(f"3. GET /analysis/history (no token) -> Status: {r3.status_code}, Body: {r3.text.strip()}")
except Exception as e:
    print(f"3. GET /analysis/history -> Error: {e}")

# 4. Check debug errors endpoint
try:
    r4 = requests.get(f"{base_url}/analysis/debug_errors", timeout=120)
    print(f"4. GET /analysis/debug_errors -> Status: {r4.status_code}, Body: {r4.text.strip()}")
except Exception as e:
    print(f"4. GET /analysis/debug_errors -> Error: {e}")
