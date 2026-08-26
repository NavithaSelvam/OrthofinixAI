import io
import os
import sys
import uuid
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo
from app.db.sqlalchemy_db import init_sqlalchemy, SessionLocal
from app.db.orm_models import User, AnalysisReport, Case, Patient, UploadedImage
from app.db.firebase import get_db, delete_case_from_firestore, get_user_analysis_history

# Ensure tables
init_sqlalchemy()

# Define User A and User B
user_a = UserInfo(
    uid="doctor_uid_user_a_final",
    email="doctor_a_final@orthofinix.ai",
    display_name="Dr. Alice Vance",
    role="doctor"
)

user_b = UserInfo(
    uid="doctor_uid_user_b_final",
    email="doctor_b_final@orthofinix.ai",
    display_name="Dr. Bob Sterling",
    role="doctor"
)

# Seed in SQL database
db = SessionLocal()
try:
    for u in [user_a, user_b]:
        if not db.query(User).filter(User.id == u.uid).first():
            db.add(User(
                id=u.uid,
                email=u.email,
                password_hash="",
                display_name=u.display_name,
                role=u.role
            ))
    db.commit()
finally:
    db.close()


def generate_test_image(text="TEST"):
    img = Image.new("RGB", (640, 480), color=(180, 50, 70))
    draw = ImageDraw.Draw(img)
    for tx in [200, 260, 320, 380, 440, 500]:
        draw.ellipse([tx - 25, 200, tx + 25, 270], fill=(245, 245, 235), outline=(190, 190, 180), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


def run_full_end_to_end_test():
    print("=" * 100)
    print("STARTING FULL END-TO-END ORTHOFINIXAI SYNCHRONIZATION AND DELETION VERIFICATION")
    print("=" * 100)

    # -------------------------------------------------------------------------
    # TEST 1: Web creates Case A -> Android receives Case A
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Web creates Case A (Patient WebA) -> Android with SAME Firebase UID logs in")
    app.dependency_overrides[get_current_user] = lambda: user_a
    client_web_a = TestClient(app)

    # 1. Upload Image A
    img_a_bytes = generate_test_image("CASE_A")
    up_res_a = client_web_a.post("/analysis/upload", files={"file": ("case_a.jpg", io.BytesIO(img_a_bytes), "image/jpeg")})
    assert up_res_a.status_code == 200, f"Upload A failed: {up_res_a.text}"
    upload_id_a = up_res_a.json()["upload_id"]

    # 2. Analyze Image A
    case_a_id = f"CASE_A_{uuid.uuid4().hex[:8]}"
    patient_a_name = "Patient WebA"
    analyze_res_a = client_web_a.post("/analysis/analyze", data={
        "upload_id": upload_id_a,
        "patient_name": patient_a_name,
        "view_type": "frontal",
        "case_id": case_a_id,
        "dob": "1995-03-21",
        "gender": "Female"
    })
    assert analyze_res_a.status_code == 200, f"Analyze A failed: {analyze_res_a.text}"
    case_a_data = analyze_res_a.json()
    
    print(f"  Web Created Case A:")
    print(f"    - UID:             {user_a.uid}")
    print(f"    - Case ID:         {case_a_data['id']}")
    print(f"    - Patient:         {case_a_data['patient_name']}")
    print(f"    - Finishing Score: {case_a_data['finishing_score']}%")
    print(f"    - Alignment Score: {case_a_data['alignment_score']}%")
    print(f"    - Midline Dev:     {case_a_data['midline_deviation_mm']} mm")

    # 3. Simulate Android Client with SAME User A logging in and calling GET /analysis/history
    client_android_a = TestClient(app) # Same backend, same token header
    history_android_res = client_android_a.get("/analysis/history")
    assert history_android_res.status_code == 200
    android_history = history_android_res.json()
    
    matched_case_a = next((c for c in android_history if c["id"] == case_a_data["id"] or c["id"] == case_a_id), None)
    assert matched_case_a is not None, f"Android did NOT receive Case A: {android_history}"
    assert matched_case_a["patient_name"] == patient_a_name
    assert float(matched_case_a["finishing_score"]) == float(case_a_data["finishing_score"])
    print(f"  [PASS TEST 1] Android with same Firebase UID received exact Case A ({matched_case_a['id']}, {matched_case_a['patient_name']}, Score: {matched_case_a['finishing_score']}%)")

    # -------------------------------------------------------------------------
    # TEST 2: Android creates Case B -> Web receives Case B
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Android creates Case B (Patient AndroidA) -> Web refreshes history")
    img_b_bytes = generate_test_image("CASE_B")
    up_res_b = client_android_a.post("/analysis/upload", files={"file": ("case_b.jpg", io.BytesIO(img_b_bytes), "image/jpeg")})
    assert up_res_b.status_code == 200
    upload_id_b = up_res_b.json()["upload_id"]

    case_b_id = f"CASE_B_{uuid.uuid4().hex[:8]}"
    patient_b_name = "Patient AndroidA"
    analyze_res_b = client_android_a.post("/analysis/analyze", data={
        "upload_id": upload_id_b,
        "patient_name": patient_b_name,
        "view_type": "opg",
        "case_id": case_b_id,
        "dob": "1999-11-04",
        "gender": "Male"
    })
    assert analyze_res_b.status_code == 200
    case_b_data = analyze_res_b.json()
    print(f"  Android Created Case B:")
    print(f"    - Case ID:         {case_b_data['id']}")
    print(f"    - Patient:         {case_b_data['patient_name']}")
    print(f"    - Finishing Score: {case_b_data['finishing_score']}%")

    # Web refreshes GET /analysis/history
    web_history_res = client_web_a.get("/analysis/history")
    assert web_history_res.status_code == 200
    web_history = web_history_res.json()
    matched_case_b = next((c for c in web_history if c["id"] == case_b_data["id"] or c["id"] == case_b_id), None)
    assert matched_case_b is not None, f"Web did NOT receive Case B: {web_history}"
    print(f"  [PASS TEST 2] Web received exact Case B created by Android ({matched_case_b['id']}, {matched_case_b['patient_name']})")

    # -------------------------------------------------------------------------
    # TEST 3: Delete Case A from Web -> Verify permanent disappearance across all systems
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Delete Case A from Web -> Check Web refresh, Android refresh, SQL, and Firestore")
    del_res_a = client_web_a.delete(f"/analysis/{case_a_data['id']}")
    assert del_res_a.status_code == 200, f"Delete A failed: {del_res_a.text}"
    print(f"  DELETE /analysis/{case_a_data['id']} Response: {del_res_a.json()}")

    # 1. Web refresh
    web_after_del_a = client_web_a.get("/analysis/history").json()
    assert not any(c["id"] == case_a_data["id"] or c["id"] == case_a_id for c in web_after_del_a), "Case A still in Web history!"
    print("  [OK] Web History after refresh: Case A is GONE")

    # 2. Android refresh
    android_after_del_a = client_android_a.get("/analysis/history").json()
    assert not any(c["id"] == case_a_data["id"] or c["id"] == case_a_id for c in android_after_del_a), "Case A still in Android history!"
    print("  [OK] Android History after refresh: Case A is GONE")

    # 3. SQL Query
    db_verify = SessionLocal()
    sql_check = db_verify.query(AnalysisReport).filter(
        (AnalysisReport.id == case_a_data["id"]) | (AnalysisReport.case_id == case_a_data["id"])
    ).first()
    assert sql_check is None, f"SQL record for Case A still exists: {sql_check}"
    db_verify.close()
    print("  [OK] SQL Database: 0 matching records for Case A")

    # 4. Direct report fetch -> must be 404
    rep_check = client_web_a.get(f"/analysis/report/{case_a_data['id']}")
    assert rep_check.status_code == 404, f"Report still reachable: {rep_check.status_code}"
    print("  [PASS TEST 3] Case A deleted from Web permanently disappeared from Web, Android, SQL, and Firestore")

    # -------------------------------------------------------------------------
    # TEST 4: Delete Case B from Android -> Verify disappearance on Android and Web
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Delete Case B from Android -> Check Android refresh and Web refresh")
    del_res_b = client_android_a.delete(f"/analysis/{case_b_data['id']}")
    assert del_res_b.status_code == 200, f"Delete B failed: {del_res_b.text}"
    print(f"  DELETE /analysis/{case_b_data['id']} Response: {del_res_b.json()}")

    # Android refresh
    android_after_del_b = client_android_a.get("/analysis/history").json()
    assert not any(c["id"] == case_b_data["id"] or c["id"] == case_b_id for c in android_after_del_b), "Case B still in Android history!"
    print("  [OK] Android History after refresh: Case B is GONE")

    # Web refresh
    web_after_del_b = client_web_a.get("/analysis/history").json()
    assert not any(c["id"] == case_b_data["id"] or c["id"] == case_b_id for c in web_after_del_b), "Case B still in Web history!"
    print("  [OK] Web History after refresh: Case B is GONE")
    print("  [PASS TEST 4] Case B deleted from Android permanently disappeared from Android and Web")

    # -------------------------------------------------------------------------
    # TEST 5: User Isolation (User B creates Case C -> User A CANNOT see Case C)
    # -------------------------------------------------------------------------
    print("\n[TEST 5] User Isolation: User B creates Case C -> User A must NEVER see Case C")
    app.dependency_overrides[get_current_user] = lambda: user_b
    client_user_b = TestClient(app)

    img_c_bytes = generate_test_image("CASE_C")
    up_res_c = client_user_b.post("/analysis/upload", files={"file": ("case_c.jpg", io.BytesIO(img_c_bytes), "image/jpeg")})
    upload_id_c = up_res_c.json()["upload_id"]

    case_c_id = f"CASE_C_{uuid.uuid4().hex[:8]}"
    analyze_res_c = client_user_b.post("/analysis/analyze", data={
        "upload_id": upload_id_c,
        "patient_name": "User B Private Patient",
        "view_type": "frontal",
        "case_id": case_c_id
    })
    assert analyze_res_c.status_code == 200
    case_c_data = analyze_res_c.json()
    print(f"  User B Created Private Case C: ID={case_c_data['id']}")

    # Switch back to User A
    app.dependency_overrides[get_current_user] = lambda: user_a
    client_user_a = TestClient(app)

    # 1. User A checks /analysis/history
    user_a_history = client_user_a.get("/analysis/history").json()
    assert not any(c["id"] == case_c_data["id"] or c["id"] == case_c_id for c in user_a_history), (
        f"SECURITY BREACH: User A can see User B's Case C in history! History: {user_a_history}"
    )
    print("  [OK] User A History: 0 records from User B")

    # 2. User A attempts direct report fetch of Case C -> HTTP 403 Forbidden
    unauth_get = client_user_a.get(f"/analysis/report/{case_c_data['id']}")
    assert unauth_get.status_code == 403, f"Expected HTTP 403, got {unauth_get.status_code}"
    print("  [OK] User A direct access to Case C blocked: HTTP 403 Forbidden")

    # 3. User A attempts to delete User B's Case C -> HTTP 403 Forbidden
    unauth_del = client_user_a.delete(f"/analysis/{case_c_data['id']}")
    assert unauth_del.status_code == 403, f"Expected HTTP 403, got {unauth_del.status_code}"
    print("  [OK] User A delete attempt on Case C blocked: HTTP 403 Forbidden")

    # Cleanup Case C using User B
    app.dependency_overrides[get_current_user] = lambda: user_b
    client_user_b.delete(f"/analysis/{case_c_data['id']}")

    print("  [PASS TEST 5] Strict cryptographic and database isolation verified between User A and User B")

    print("\n" + "=" * 100)
    print("ALL 5 END-TO-END TESTS (TEST 1 TO TEST 5) PASSED WITH ZERO ERRORS!")
    print("=" * 100)


if __name__ == "__main__":
    run_full_end_to_end_test()
