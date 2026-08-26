import sys
import os
import io
import json
import uuid
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo

# Doctor Users
doctor_a = UserInfo(
    uid="firebase_user_a_uid_12345",
    email="doctor.alice@orthofinix.ai",
    display_name="Dr. Alice Smith",
    role="doctor",
    hospital="Orthofinix Clinic",
    is_active=True,
    is_verified=True
)

doctor_b = UserInfo(
    uid="firebase_user_b_uid_67890",
    email="doctor.bob@orthofinix.ai",
    display_name="Dr. Bob Jones",
    role="doctor",
    hospital="Orthofinix Clinic",
    is_active=True,
    is_verified=True
)

active_user = doctor_a

def get_test_user():
    return active_user

app.dependency_overrides[get_current_user] = get_test_user
client = TestClient(app)

def create_sample_image():
    from PIL import ImageDraw
    img = Image.new("RGB", (640, 480), color=(170, 70, 80))
    draw = ImageDraw.Draw(img)
    upper_x = [140, 180, 220, 260, 300, 340, 380, 420, 460, 500]
    for x in upper_x:
        draw.rounded_rectangle([x - 16, 160, x + 16, 235], radius=5, fill=(245, 245, 235), outline=(140, 140, 140))
    lower_x = [150, 190, 230, 270, 305, 335, 370, 410, 450, 490]
    for x in lower_x:
        draw.rounded_rectangle([x - 14, 250, x + 14, 315], radius=5, fill=(240, 240, 230), outline=(140, 140, 140))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    buf.seek(0)
    return buf

def test_full_cross_platform_synchronization_and_isolation():
    global active_user

    print("\n=================================================================")
    print("STEP 3: TESTING CROSS-PLATFORM SYNCHRONIZATION & USER ISOLATION")
    print("=================================================================")

    # ==========================================================
    # TEST 1: Android Client creates Case A -> Web Client receives Case A
    # ==========================================================
    print("\n[TEST 1] Android creates Case A (Patient: Alice Cooper) -> Web queries User A history")
    active_user = doctor_a

    # 1a. Upload image as Android client
    img_a = create_sample_image()
    upload_res_a = client.post("/analysis/upload", files={"file": ("android_case_a.jpg", img_a, "image/jpeg")})
    assert upload_res_a.status_code == 200, f"Upload A failed: {upload_res_a.text}"
    upload_id_a = upload_res_a.json()["upload_id"]

    # 1b. Analyze as Android client
    case_a_id = f"CASE_ANDROID_{uuid.uuid4().hex[:8]}"
    payload_a = {
        "upload_id": upload_id_a,
        "patient_name": "Alice Cooper",
        "view_type": "opg",
        "case_id": case_a_id,
        "dob": "1995-03-15",
        "gender": "Female",
        "notes": "Created via Android Client"
    }
    analyze_res_a = client.post("/analysis/analyze", data=payload_a)
    assert analyze_res_a.status_code == 200, f"Analyze A failed: {analyze_res_a.text}"
    report_a = analyze_res_a.json()
    assert report_a["id"] == case_a_id
    assert report_a["patient_name"] == "Alice Cooper"
    assert report_a["finishing_score"] > 0
    print(f" -> Case A created by Android: ID={case_a_id}, Score={report_a['finishing_score']:.1f}%")

    # 1c. Web client logs in as User A and queries /analysis/history
    web_history_res_1 = client.get("/analysis/history")
    assert web_history_res_1.status_code == 200
    web_cases_1 = web_history_res_1.json()
    case_a_found = next((c for c in web_cases_1 if c["id"] == case_a_id), None)
    assert case_a_found is not None, "Case A was NOT found in Web history for User A!"
    assert case_a_found["patient_name"] == "Alice Cooper"
    print(f" -> [PASS] Web Client retrieved Case A for User A: {case_a_found['patient_name']} (ID: {case_a_found['id']})")

    # ==========================================================
    # TEST 2: Web Client creates Case B -> Android Client receives Case B
    # ==========================================================
    print("\n[TEST 2] Web creates Case B (Patient: Bob Anderson) -> Android queries User A history")
    active_user = doctor_a

    # 2a. Upload image as Web client
    img_b = create_sample_image()
    upload_res_b = client.post("/analysis/upload", files={"file": ("web_case_b.jpg", img_b, "image/jpeg")})
    assert upload_res_b.status_code == 200, f"Upload B failed: {upload_res_b.text}"
    upload_id_b = upload_res_b.json()["upload_id"]

    # 2b. Analyze as Web client
    case_b_id = f"CASE_WEB_{uuid.uuid4().hex[:8]}"
    payload_b = {
        "upload_id": upload_id_b,
        "patient_name": "Bob Anderson",
        "view_type": "opg",
        "case_id": case_b_id,
        "dob": "1988-11-22",
        "gender": "Male",
        "notes": "Created via Web Client"
    }
    analyze_res_b = client.post("/analysis/analyze", data=payload_b)
    assert analyze_res_b.status_code == 200, f"Analyze B failed: {analyze_res_b.text}"
    report_b = analyze_res_b.json()
    assert report_b["id"] == case_b_id
    assert report_b["patient_name"] == "Bob Anderson"
    print(f" -> Case B created by Web: ID={case_b_id}, Score={report_b['finishing_score']:.1f}%")

    # 2c. Android client fetches history for User A
    android_history_res_2 = client.get("/analysis/history")
    assert android_history_res_2.status_code == 200
    android_cases_2 = android_history_res_2.json()
    case_b_found = next((c for c in android_cases_2 if c["id"] == case_b_id), None)
    assert case_b_found is not None, "Case B was NOT found in Android history for User A!"
    assert case_b_found["patient_name"] == "Bob Anderson"
    print(f" -> [PASS] Android Client retrieved Case B for User A: {case_b_found['patient_name']} (ID: {case_b_found['id']})")

    # Both Case A and Case B exist for User A
    user_a_ids = [c["id"] for c in android_cases_2]
    assert case_a_id in user_a_ids and case_b_id in user_a_ids
    print(f" -> User A currently has {len(user_a_ids)} synchronized cases across Android & Web.")

    # ==========================================================
    # TEST 3: User B creates Case C -> Case Isolation Check
    # ==========================================================
    print("\n[TEST 3] User B (Dr. Bob) creates Case C -> Verify User A cannot see Case C & User B cannot see Case A/B")
    active_user = doctor_b

    # 3a. User B creates Case C
    img_c = create_sample_image()
    upload_res_c = client.post("/analysis/upload", files={"file": ("user_b_case_c.jpg", img_c, "image/jpeg")})
    assert upload_res_c.status_code == 200
    upload_id_c = upload_res_c.json()["upload_id"]

    case_c_id = f"CASE_USER_B_{uuid.uuid4().hex[:8]}"
    payload_c = {
        "upload_id": upload_id_c,
        "patient_name": "Charlie Davis",
        "view_type": "opg",
        "case_id": case_c_id,
        "dob": "2001-08-09",
        "gender": "Male",
        "notes": "Private case of Doctor B"
    }
    analyze_res_c = client.post("/analysis/analyze", data=payload_c)
    assert analyze_res_c.status_code == 200
    print(f" -> Case C created by User B: ID={case_c_id}, Patient=Charlie Davis")

    # 3b. User B fetches history -> Case C present, Case A and Case B ABSENT
    user_b_history = client.get("/analysis/history").json()
    user_b_ids = [c["id"] for c in user_b_history]
    assert case_c_id in user_b_ids, "User B should see Case C"
    assert case_a_id not in user_b_ids, "LEAK DETECTED: User B saw Case A belonging to User A!"
    assert case_b_id not in user_b_ids, "LEAK DETECTED: User B saw Case B belonging to User A!"
    print(f" -> [PASS] User B history is completely isolated: only contains User B's {len(user_b_ids)} case(s).")

    # 3c. Switch back to User A -> Case A & B present, Case C ABSENT
    active_user = doctor_a
    user_a_history = client.get("/analysis/history").json()
    user_a_ids_after = [c["id"] for c in user_a_history]
    assert case_a_id in user_a_ids_after, "User A must see Case A"
    assert case_b_id in user_a_ids_after, "User A must see Case B"
    assert case_c_id not in user_a_ids_after, "LEAK DETECTED: User A saw Case C belonging to User B!"
    print(f" -> [PASS] User A history is completely isolated: Case C does NOT appear for User A.")

    # ==========================================================
    # TEST 4: Integrity Verification (No Overwrite Between Cases)
    # ==========================================================
    print("\n[TEST 4] Verify individual case integrity, metrics, and parameters")
    rep_a_res = client.get(f"/analysis/report/{case_a_id}")
    rep_b_res = client.get(f"/analysis/report/{case_b_id}")
    assert rep_a_res.status_code == 200
    assert rep_b_res.status_code == 200
    data_a = rep_a_res.json()
    data_b = rep_b_res.json()

    assert data_a["id"] == case_a_id
    assert data_a["patient_name"] == "Alice Cooper"
    assert data_b["id"] == case_b_id
    assert data_b["patient_name"] == "Bob Anderson"
    assert data_a["id"] != data_b["id"]
    assert data_a["patient_name"] != data_b["patient_name"]
    print(f" -> [PASS] Case A ({data_a['patient_name']}) and Case B ({data_b['patient_name']}) retain independent records.")

    print("\n=================================================================")
    print("ALL 4 SYNCHRONIZATION AND ISOLATION TESTS PASSED SUCCESSFULLY!")
    print("=================================================================\n")

if __name__ == "__main__":
    test_full_cross_platform_synchronization_and_isolation()
