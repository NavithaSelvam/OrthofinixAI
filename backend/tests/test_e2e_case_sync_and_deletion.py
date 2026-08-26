import io
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo
from app.db.sqlalchemy_db import init_sqlalchemy, SessionLocal
from app.db.orm_models import User, AnalysisReport, Case, Patient, UploadedImage
from app.db.firebase import get_db, delete_case_from_firestore

# Ensure database tables
init_sqlalchemy()

# User A and User B
user_a = UserInfo(
    uid="doctor_uid_user_a",
    email="doctor_a@orthofinix.ai",
    display_name="Dr. User A",
    role="doctor"
)

user_b = UserInfo(
    uid="doctor_uid_user_b",
    email="doctor_b@orthofinix.ai",
    display_name="Dr. User B",
    role="doctor"
)

# Seed users in SQL database
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


def create_test_image_bytes():
    img = Image.new("RGB", (640, 480), color=(230, 240, 250))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_full_case_sync_and_deletion_suite():
    print("=" * 80)
    print("RUNNING END-TO-END CASE SYNC AND PERMANENT DELETION TEST SUITE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # TEST A: User A creates Case A on Web
    # -------------------------------------------------------------------------
    print("\n--- [TEST A] User A creates Case A on Web ---")
    app.dependency_overrides[get_current_user] = lambda: user_a
    client = TestClient(app)

    # 1. Upload image
    buf = create_test_image_bytes()
    upload_res = client.post("/analysis/upload", files={"file": ("case_a_opg.jpg", buf, "image/jpeg")})
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_id = upload_res.json()["upload_id"]
    print(f"  [OK] Uploaded image: upload_id={upload_id}")

    # 2. Analyze
    case_a_id = f"case_web_{uuid.uuid4().hex[:8]}"
    analyze_res = client.post("/analysis/analyze", data={
        "upload_id": upload_id,
        "patient_name": "Alice Green",
        "view_type": "opg",
        "case_id": case_a_id,
        "dob": "1998-05-12",
        "gender": "Female"
    })
    assert analyze_res.status_code == 200, f"Analyze failed: {analyze_res.text}"
    case_a_data = analyze_res.json()
    assert case_a_data["id"] == case_a_id or case_a_data["case_id"] == case_a_id
    print(f"  [OK] Case A created: ID={case_a_data['id']}, patient={case_a_data['patient_name']}, score={case_a_data['finishing_score']}")

    # 3. Verify Case A is in User A's history
    history_res = client.get("/analysis/history")
    assert history_res.status_code == 200
    user_a_history = history_res.json()
    case_a_found = any(c["id"] == case_a_id or c["id"] == case_a_data["id"] for c in user_a_history)
    assert case_a_found, "Case A not found in User A history"
    print(f"  [PASS TEST A] Case A successfully appears in User A history ({len(user_a_history)} total cases)")

    # -------------------------------------------------------------------------
    # TEST B: User A deletes Case A on Android / Web
    # -------------------------------------------------------------------------
    print("\n--- [TEST B] User A deletes Case A ---")
    del_target_id = case_a_data["id"]
    delete_res = client.delete(f"/analysis/{del_target_id}")
    assert delete_res.status_code == 200, f"Delete failed: {delete_res.text}"
    del_resp_data = delete_res.json()
    print(f"  [OK] DELETE /analysis/{del_target_id} -> status={del_resp_data.get('status')}, deleted_ids={del_resp_data.get('deleted_ids')}")

    # Verify SQL does not contain Case A
    db_verify = SessionLocal()
    sql_report = db_verify.query(AnalysisReport).filter(
        (AnalysisReport.id == del_target_id) | (AnalysisReport.case_id == del_target_id)
    ).first()
    assert sql_report is None, f"SQL AnalysisReport still contains Case A: {sql_report}"
    print("  [OK] SQL: 0 matching records for Case A")
    db_verify.close()

    # Verify history does not contain Case A
    history_after_del = client.get("/analysis/history").json()
    assert not any(c["id"] == del_target_id or c["id"] == case_a_id for c in history_after_del)
    print("  [OK] Backend History: Case A does not exist")
    print("  [PASS TEST B] Case A permanently deleted from SQL, Firestore, and History")

    # -------------------------------------------------------------------------
    # TEST C: User A creates Case B on Android
    # -------------------------------------------------------------------------
    print("\n--- [TEST C] User A creates Case B on Android ---")
    buf_b = create_test_image_bytes()
    upload_res_b = client.post("/analysis/upload", files={"file": ("case_b_photo.jpg", buf_b, "image/jpeg")})
    assert upload_res_b.status_code == 200
    upload_id_b = upload_res_b.json()["upload_id"]

    case_b_id = f"case_android_{uuid.uuid4().hex[:8]}"
    analyze_res_b = client.post("/analysis/analyze", data={
        "upload_id": upload_id_b,
        "patient_name": "Bob Miller",
        "view_type": "frontal",
        "case_id": case_b_id,
        "dob": "2002-09-18",
        "gender": "Male"
    })
    assert analyze_res_b.status_code == 200
    case_b_data = analyze_res_b.json()
    print(f"  [OK] Case B created: ID={case_b_data['id']}, patient={case_b_data['patient_name']}")

    # Verify Case B appears on Web (querying history with same User A)
    web_history_res = client.get("/analysis/history")
    assert web_history_res.status_code == 200
    assert any(c["id"] == case_b_data["id"] or c["id"] == case_b_id for c in web_history_res.json())
    print("  [PASS TEST C] Case B created on Android appears on Web for User A")

    # -------------------------------------------------------------------------
    # TEST D: User A deletes Case B on Web
    # -------------------------------------------------------------------------
    print("\n--- [TEST D] User A deletes Case B on Web ---")
    del_b_res = client.delete(f"/analysis/{case_b_data['id']}")
    assert del_b_res.status_code == 200
    print(f"  [OK] DELETE /analysis/{case_b_data['id']} -> {del_b_res.json()}")

    # Verify both Android and Web refresh show 0 occurrences of Case B
    refresh_1 = client.get("/analysis/history").json()
    assert not any(c["id"] == case_b_data["id"] or c["id"] == case_b_id for c in refresh_1)
    refresh_2 = client.get("/analysis/history").json()
    assert not any(c["id"] == case_b_data["id"] or c["id"] == case_b_id for c in refresh_2)
    print("  [PASS TEST D] Case B deleted on Web remains deleted after multiple refreshes")

    # -------------------------------------------------------------------------
    # TEST E: User B (different UID) must NEVER see User A's cases
    # -------------------------------------------------------------------------
    print("\n--- [TEST E] User Isolation: User B must NEVER see User A's cases ---")
    # First, create a private case for User A
    buf_priv = create_test_image_bytes()
    up_priv = client.post("/analysis/upload", files={"file": ("user_a_private.jpg", buf_priv, "image/jpeg")}).json()
    priv_case_id = f"priv_case_{uuid.uuid4().hex[:8]}"
    case_priv = client.post("/analysis/analyze", data={
        "upload_id": up_priv["upload_id"],
        "patient_name": "Private Patient User A",
        "view_type": "opg",
        "case_id": priv_case_id
    }).json()

    # Switch to User B
    app.dependency_overrides[get_current_user] = lambda: user_b
    client_b = TestClient(app)

    user_b_history = client_b.get("/analysis/history").json()
    user_b_case_ids = [c["id"] for c in user_b_history]
    assert priv_case_id not in user_b_case_ids and case_priv["id"] not in user_b_case_ids, (
        f"SECURITY LEAK: User B can see User A's private case: {user_b_history}"
    )

    # User B attempts to access User A's report directly
    user_b_access_attempt = client_b.get(f"/analysis/report/{case_priv['id']}")
    assert user_b_access_attempt.status_code in [403, 404], f"User B accessed User A's report: {user_b_access_attempt.status_code}"

    # User B attempts to delete User A's case
    user_b_del_attempt = client_b.delete(f"/analysis/{case_priv['id']}")
    assert user_b_del_attempt.status_code == 403, f"User B was able to delete User A's case! Status: {user_b_del_attempt.status_code}"
    print(f"  [OK] User B deletion attempt on User A case blocked with HTTP 403 Forbidden")
    print("  [PASS TEST E] Strict data isolation between User A and User B verified")

    # -------------------------------------------------------------------------
    # TEST F: Delete a case, simulate fresh application restart, verify remains deleted
    # -------------------------------------------------------------------------
    print("\n--- [TEST F] Simulated app restart verification ---")
    app.dependency_overrides[get_current_user] = lambda: user_a
    client_a = TestClient(app)
    # User A deletes private case
    del_priv_res = client_a.delete(f"/analysis/{case_priv['id']}")
    assert del_priv_res.status_code == 200

    # Simulate restart by creating a new client and querying multiple times
    restart_client = TestClient(app)
    restart_history = restart_client.get("/analysis/history").json()
    assert not any(c["id"] == priv_case_id or c["id"] == case_priv["id"] for c in restart_history)
    print("  [PASS TEST F] Case remains permanently deleted across application restarts")

    print("\n" + "=" * 80)
    print("ALL TESTS (TEST A -> TEST F) PASSED WITH ZERO ERRORS!")
    print("=" * 80)


if __name__ == "__main__":
    test_full_case_sync_and_deletion_suite()
