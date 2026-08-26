import os
import sys
import uuid
from io import BytesIO
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.firebase_service import (
    init_firebase_admin,
    get_firestore_client,
    get_storage_bucket,
    upload_clinical_image,
    save_case_analysis,
)

def create_dummy_image_bytes() -> bytes:
    img = Image.new("RGB", (200, 200), color=(56, 189, 248))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_firebase_storage_and_firestore_link():
    print("\n========================================================")
    print("Testing Firebase Cloud Storage & Firestore Integration")
    print("========================================================")

    init_firebase_admin()
    db = get_firestore_client()
    bucket = get_storage_bucket()
    print(f"[1] Connected to Firebase Storage Bucket: {bucket.name}")

    test_uid = f"doctor_{uuid.uuid4().hex[:8]}"
    test_filename = f"clinical_opg_{uuid.uuid4().hex[:8]}.jpg"
    test_image_bytes = create_dummy_image_bytes()

    print(f"\n[2] Uploading image to cases/{test_uid}/{test_filename}...")
    image_url = upload_clinical_image(
        file_bytes=test_image_bytes,
        filename=test_filename,
        uid=test_uid,
        content_type="image/jpeg"
    )
    assert image_url is not None and len(image_url) > 0, "Upload failed to return an image URL"
    print(f"    CONFIRMED Storage Download URL: {image_url}")

    test_case_id = f"case_storage_{uuid.uuid4().hex[:8]}"
    test_report_data = {
        "id": test_case_id,
        "case_id": test_case_id,
        "patient_name": "Eleanor Vance",
        "image_url": image_url,
        "finishing_score": 91.0,
        "abo_score": 88.0,
        "andrews_score": 92.0,
        "root_angulation_score": 87.0,
        "alignment_score": 94.0,
        "confidence_score": 0.96,
        "prediction": "Optimal Class I occlusion with favorable root angulation.",
        "recommendations": ["Maintain current retention protocol."],
        "metrics": {"overjet_mm": 2.0, "overbite_percent": 24.0},
        "view_type": "opg"
    }

    print(f"\n[3] Saving Case Analysis with image_url to Firestore 'analyses'...")
    saved_doc = save_case_analysis(
        uid=test_uid,
        filename=test_filename,
        report_data=test_report_data
    )
    assert saved_doc["image_url"] == image_url

    print(f"\n[4] Verifying Firestore 'analyses' document contains storage image_url...")
    analyses_doc = db.collection("analyses").document(test_case_id).get()
    assert analyses_doc.exists, f"Document analyses/{test_case_id} was not found!"
    doc_dict = analyses_doc.to_dict()
    assert doc_dict.get("image_url") == image_url, f"Stored URL mismatch! Expected: {image_url}, Got: {doc_dict.get('image_url')}"
    print(f"    CONFIRMED Firestore analyses/{test_case_id}")
    print(f"    Persisted image_url: {doc_dict.get('image_url')}")
    print(f"    ABO Score: {doc_dict.get('abo_score')}, Finishing Score: {doc_dict.get('finishing_score')}")

    print("\n[5] Cleaning up test artifacts...")
    try:
        db.collection("analyses").document(test_case_id).delete()
        db.collection("cases").document(test_case_id).delete()
        db.collection("analysis_reports").document(test_case_id).delete()
        db.collection("users").document(test_uid).delete()
        print("    Cleaned up test Firestore documents.")
    except Exception as e:
        print(f"    Notice during cleanup: {e}")

    print("\n========================================================")
    print("ALL STORAGE & FIRESTORE TESTS PASSED SUCCESSFULLY!")
    print("========================================================\n")

if __name__ == "__main__":
    test_firebase_storage_and_firestore_link()
