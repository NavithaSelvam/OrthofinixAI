import urllib.request
import json

def fetch_errors():
    url = "https://orthofinixai-backend.onrender.com/analysis/debug_errors"
    try:
        with urllib.request.urlopen(url) as r:
            errors = json.loads(r.read().decode())
            print(f"RECENT ERRORS (Count: {len(errors)}):")
            for idx, err in enumerate(errors):
                print(f"\n--- ERROR #{idx+1} ---")
                print("Error Message:", err.get("error"))
                print("Traceback:")
                print(err.get("traceback"))
    except Exception as e:
        print("Failed to fetch errors:", e)

if __name__ == "__main__":
    fetch_errors()
