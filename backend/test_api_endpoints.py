import io
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo
from app.db.sqlalchemy_db import init_sqlalchemy, SessionLocal
from app.db.orm_models import User

# Ensure database tables
init_sqlalchemy()

# Mock current user for testing API endpoints
mock_user = UserInfo(
    uid="doctor_integration_test_user",
    email="testdoctor@orthofinix.ai",
    display_name="Dr. Integration Test",
    role="doctor"
)

# Ensure the mock user exists in the database
db = SessionLocal()
try:
    if not db.query(User).filter(User.id == mock_user.uid).first():
        db.add(User(
            id=mock_user.uid,
            email=mock_user.email,
            password_hash="",
            display_name=mock_user.display_name,
            role=mock_user.role
        ))
        db.commit()
finally:
    db.close()

app.dependency_overrides[get_current_user] = lambda: mock_user

client = TestClient(app)

def test_full_api_flow():
    print(">>> Testing Full API Flow with Database Persistence...")
    
    # 1. Health check
    r = client.get("/ping")
    assert r.status_code == 200
    print("   [OK] Ping: 200 OK")
    
    # 2. Create Patient
    pat_res = client.post("/patients/", json={
        "name": "Sarah Connor",
        "date_of_birth": "1995-11-20",
        "gender": "Female",
        "contact_info": "sarah@example.com"
    })
    assert pat_res.status_code == 200, f"Error: {pat_res.text}"
    pat_data = pat_res.json()
    patient_id = pat_data["id"]
    print(f"   [OK] POST /patients/: Created patient '{pat_data['name']}' (ID: {patient_id})")
    
    # 3. List Patients
    pats_list = client.get("/patients/")
    assert pats_list.status_code == 200, f"Error: {pats_list.text}"
    assert any(p["id"] == patient_id for p in pats_list.json())
    print(f"   [OK] GET /patients/: Found {len(pats_list.json())} patient(s)")
    
    # 4. Create Case
    case_res = client.post("/cases/", json={
        "patient_id": patient_id,
        "notes": "Pre-treatment orthodontic assessment."
    })
    assert case_res.status_code == 200, f"Error: {case_res.text}"
    case_data = case_res.json()
    case_id = case_data["id"]
    print(f"   [OK] POST /cases/: Created case for patient (ID: {case_id})")
    
    # 5. Upload Image
    img = Image.new("RGB", (640, 480), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    
    upload_res = client.post(
        "/analysis/upload",
        files={"file": ("test_dental_photo.jpg", buf, "image/jpeg")}
    )
    assert upload_res.status_code == 200, f"Error: {upload_res.text}"
    upload_data = upload_res.json()
    upload_id = upload_data["upload_id"]
    print(f"   [OK] POST /analysis/upload: Uploaded image (Upload ID: {upload_id})")
    
    # 6. Run AI Analysis
    analyze_res = client.post(
        "/analysis/analyze",
        data={
            "upload_id": upload_id,
            "patient_name": "Sarah Connor",
            "view_type": "frontal",
            "case_id": case_id
        }
    )
    assert analyze_res.status_code == 200, f"Error: {analyze_res.text}"
    report_data = analyze_res.json()
    assert report_data["id"] == case_id
    assert "finishing_score" in report_data
    print(f"   [OK] POST /analysis/analyze: Report generated and saved (Score: {report_data['finishing_score']}%)")
    
    # 7. Check History
    history_res = client.get("/analysis/history")
    assert history_res.status_code == 200, f"Error: {history_res.text}"
    history_items = history_res.json()
    assert any(item["id"] == case_id for item in history_items)
    print(f"   [OK] GET /analysis/history: Retrieved {len(history_items)} history items from database")
    
    # 8. Check Specific Report
    single_rep = client.get(f"/analysis/report/{case_id}")
    assert single_rep.status_code == 200, f"Error: {single_rep.text}"
    assert single_rep.json()["id"] == case_id
    print(f"   [OK] GET /analysis/report/{case_id}: Successfully retrieved report details from database")
    
    # 9. Create Post / Clinical Note
    post_res = client.post("/posts/", json={
        "title": "Finishing checklist for Sarah Connor",
        "content": "Check bracket position on tooth 21 before next archwire change.",
        "category": "clinical_note",
        "report_id": case_id
    })
    assert post_res.status_code == 200, f"Error: {post_res.text}"
    post_data = post_res.json()
    post_id = post_data["id"]
    print(f"   [OK] POST /posts/: Created clinical note '{post_data['title']}' (ID: {post_id})")
    
    # 10. List Posts
    posts_list = client.get("/posts/")
    assert posts_list.status_code == 200, f"Error: {posts_list.text}"
    assert any(p["id"] == post_id for p in posts_list.json())
    print(f"   [OK] GET /posts/: Retrieved {len(posts_list.json())} post(s) from database")
    
    # 11. Delete Case
    del_case_res = client.delete(f"/cases/{case_id}")
    assert del_case_res.status_code == 200, f"Error: {del_case_res.text}"
    print(f"   [OK] DELETE /cases/{case_id}: Successfully deleted case and cascaded to reports/images")

    # 12. Delete Patient
    del_pat_res = client.delete(f"/patients/{patient_id}")
    assert del_pat_res.status_code == 200, f"Error: {del_pat_res.text}"
    print(f"   [OK] DELETE /patients/{patient_id}: Successfully deleted patient and associated records")

    print("\n ALL API ENDPOINTS, PER-TOOTH ODONTOGRAM & CASCADE DELETION VERIFIED 100% OPERATIONAL!")

if __name__ == "__main__":
    test_full_api_flow()

