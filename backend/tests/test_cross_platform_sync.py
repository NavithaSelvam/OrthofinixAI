import sys
import os
import io
import json
from datetime import datetime, timezone
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo

# Mock Doctor User
mock_doctor = UserInfo(
    uid="doc_sync_check",
    email="dr.sync.check@orthofinix.ai",
    display_name="Dr. Cross Platform Sync",
    role="doctor",
    hospital="Orthofinix Clinic",
    is_active=True,
    is_verified=True
)

# Override auth dependency for tests
app.dependency_overrides[get_current_user] = lambda: mock_doctor

client = TestClient(app)

def create_dummy_image():
    file = io.BytesIO()
    image = Image.new("RGB", (640, 480), color=(100, 150, 200))
    image.save(file, "JPEG")
    file.seek(0)
    return file

def test_full_cross_platform_pipeline():
    print("\n=======================================================")
    print("RUNNING END-TO-END CROSS-PLATFORM SYNC & PIPELINE AUDIT")
    print("=======================================================")

    # 1. Test Health / Root
    root_res = client.get("/")
    assert root_res.status_code == 200, f"Root endpoint failed: {root_res.text}"
    print("[OK] 1. Backend Health Check: PASSED")

    # 2. Test Image Upload
    img_file = create_dummy_image()
    upload_res = client.post(
        "/analysis/upload",
        files={"file": ("test_opg_audit.jpg", img_file, "image/jpeg")}
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    assert "upload_id" in upload_data, "upload_id missing from upload response"
    assert "image_url" in upload_data, "image_url missing from upload response"
    upload_id = upload_data["upload_id"]
    image_url = upload_data["image_url"]
    print(f"[OK] 2. Image Upload Endpoint: PASSED (upload_id: {upload_id})")

    # 3. Test Full Analysis Submission
    analysis_payload = {
        "upload_id": upload_id,
        "image_url": image_url,
        "view_type": "opg",
        "patient_name": "Sync Audit Patient",
        "dob": "1998-05-14",
        "gender": "Female",
        "notes": "Automated End-to-End Cross Platform Sync Audit"
    }
    analyze_res = client.post("/analysis/analyze", data=analysis_payload)
    assert analyze_res.status_code == 200, f"Analysis failed: {analyze_res.text}"
    report = analyze_res.json()
    assert "id" in report, "id missing from report response"
    assert "finishing_score" in report, "finishing_score missing from report"
    assert "abo_score" in report, "abo_score missing from report"
    assert "recommendations" in report, "recommendations missing from report"
    assert len(report["recommendations"]) > 0, "recommendations list is empty"
    report_id = report["id"]
    print(f"[OK] 3. AI Analysis Pipeline: PASSED (Report ID: {report_id}, Score: {report['finishing_score']:.1f})")

    # 4. Test Case History Retrieval (Simulating Mobile App Sync)
    history_res = client.get("/analysis/history")
    assert history_res.status_code == 200, f"History fetch failed: {history_res.text}"
    history_items = history_res.json()
    assert isinstance(history_items, list), "History items is not a list"
    matched = any(item.get("id") == report_id or item.get("patient_name") == "Sync Audit Patient" for item in history_items)
    assert matched, f"Created case {report_id} was not returned in doctor history"
    print(f"[OK] 4. Case History Sync Retrieval: PASSED ({len(history_items)} cases retrieved for doctor)")

    # 5. Test Single Report Detail Retrieval (Simulating ResultsPage)
    report_detail_res = client.get(f"/analysis/report/{report_id}")
    assert report_detail_res.status_code == 200, f"Report detail fetch failed: {report_detail_res.text}"
    detail_data = report_detail_res.json()
    assert detail_data["patient_name"] == "Sync Audit Patient", "Patient name mismatch"
    assert detail_data["id"] == report_id, "Report ID mismatch"
    print(f"[OK] 5. Single Report Detail Endpoint: PASSED (Patient: {detail_data['patient_name']})")

    # 6. Test APK Download Endpoint (Simulating Direct Phone Installation)
    apk_res = client.get("/download-apk")
    assert apk_res.status_code in [200, 307, 308], f"APK download endpoint failed: {apk_res.status_code}"
    print(f"[OK] 6. Mobile APK Distribution Endpoint: PASSED (Status: {apk_res.status_code})")

    print("=======================================================")
    print("ALL END-TO-END AUDIT & CROSS-PLATFORM CHECKS PASSED 100%")
    print("=======================================================\n")

if __name__ == "__main__":
    test_full_cross_platform_pipeline()
