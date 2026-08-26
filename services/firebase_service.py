import os
import json
import uuid
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage

_initialized = False

def init_firebase_admin(cert_path: Optional[str] = None):
    """
    Initializes the Firebase Admin SDK using firebase_service_account.json
    or any detected service account credentials file.
    """
    global _initialized
    if not firebase_admin._apps:
        possible_paths = [
            cert_path,
            os.getenv("FIREBASE_CREDENTIALS_PATH"),
            "firebase_service_account.json",
            "firebase-adminsdk.json",
            "firebase-adminsdk.json.json",
            os.path.join(os.path.dirname(__file__), "..", "firebase_service_account.json"),
            os.path.join(os.path.dirname(__file__), "..", "backend", "firebase_service_account.json"),
            os.path.join(os.path.dirname(__file__), "..", "backend", "firebase-adminsdk.json"),
            os.path.join(os.path.dirname(__file__), "..", "backend", "firebase-adminsdk.json.json"),
        ]
        
        cred = None
        for p in possible_paths:
            if p and os.path.exists(p):
                try:
                    cred = credentials.Certificate(p)
                    print(f"[Firebase Admin] Loaded credentials from: {p}")
                    break
                except Exception as e:
                    print(f"[Firebase Admin] Error loading certificate {p}: {e}")

        bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET", "orthofinixai.firebasestorage.app")
        if cred:
            firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})
        else:
            firebase_admin.initialize_app(options={'storageBucket': bucket_name})
            
    _initialized = True

# Initialize on module load
init_firebase_admin()

def get_firestore_client():
    return firestore.client()

def get_storage_bucket(bucket_name: Optional[str] = None):
    """
    Returns the Firebase Cloud Storage bucket instance.
    """
    name = bucket_name or os.getenv("FIREBASE_STORAGE_BUCKET", "orthofinixai.firebasestorage.app")
    try:
        return storage.bucket(name)
    except Exception:
        return storage.bucket()

def upload_clinical_image(
    file_bytes: bytes, 
    filename: str, 
    uid: str, 
    content_type: str = "image/jpeg"
) -> str:
    """
    Uploads clinical image bytes to Firebase Cloud Storage at 'cases/{uid}/{filename}'
    and returns a persistent, accessible download URL.
    """
    if not file_bytes:
        raise ValueError("file_bytes cannot be empty")

    clean_filename = filename if filename else f"{uuid.uuid4()}.jpg"
    clean_uid = uid.strip() if (uid and uid.strip()) else "user"
    blob_path = f"cases/{clean_uid}/{clean_filename}"

    try:
        bucket = get_storage_bucket()
        blob = bucket.blob(blob_path)

        download_token = str(uuid.uuid4())
        metadata = {
            "firebaseStorageDownloadTokens": download_token,
            "uid": clean_uid,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        blob.metadata = metadata

        blob.upload_from_string(file_bytes, content_type=content_type)

        try:
            blob.make_public()
            public_url = blob.public_url
        except Exception:
            encoded_path = urllib.parse.quote(blob_path, safe='')
            public_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={download_token}"

        print(f"[Firebase Storage] Uploaded clinical image: {blob_path} -> {public_url}")
        return public_url

    except Exception as e:
        print(f"[Firebase Storage] Upload failed for {blob_path}: {e}")
        base_url = os.getenv("PUBLIC_BASE_URL", "https://orthofinixai-backend.onrender.com")
        os.makedirs("uploads", exist_ok=True)
        local_path = os.path.join("uploads", clean_filename)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        return f"{base_url}/uploads/{clean_filename}"

def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    if not id_token:
        raise ValueError("ID token is required")
        
    try:
        decoded = auth.verify_id_token(id_token, clock_skew_seconds=10)
        return decoded
    except Exception as e:
        print(f"[Firebase Auth] Token verification failed: {e}")
        raise

def log_user_activity(uid: str, email: str = "", display_name: str = "Doctor") -> Dict[str, Any]:
    if not uid:
        return {}

    db = get_firestore_client()
    now_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "uid": uid,
        "email": email or "",
        "display_name": display_name or "Doctor",
        "last_login": now_iso,
        "last_active": now_iso,
        "updated_at": now_iso,
        "role": "doctor"
    }

    try:
        db.collection("users").document(uid).set(user_doc, merge=True)
    except Exception as e:
        print(f"[Firestore] Failed to update user profile doc for {uid}: {e}")

    try:
        log_id = str(uuid.uuid4())
        log_entry = {
            "id": log_id,
            "uid": uid,
            "email": email or "",
            "display_name": display_name or "Doctor",
            "event": "login",
            "timestamp": now_iso,
        }
        db.collection("login_logs").document(log_id).set(log_entry)
        db.collection("activity_logs").document(log_id).set(log_entry)
    except Exception as e:
        print(f"[Firestore] Failed to record login log for {uid}: {e}")

    return user_doc

def save_case_analysis(
    uid: str, 
    filename: str, 
    report_data: Dict[str, Any]
) -> Dict[str, Any]:
    db = get_firestore_client()
    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()
    now_ms = int(now_dt.timestamp() * 1000)

    case_id = report_data.get("id") or report_data.get("case_id") or str(uuid.uuid4())
    patient_name = report_data.get("patient_name") or report_data.get("patientName") or "Patient"
    clean_pname = "".join(c if c.isalnum() else "_" for c in patient_name.lower().strip())
    patient_id = report_data.get("patient_id") or report_data.get("patientId") or (f"pat_{clean_pname}_{uid[:8]}" if uid else f"pat_{clean_pname}_{case_id[:8]}")

    dob_val = report_data.get("dob") or report_data.get("date_of_birth") or report_data.get("dateOfBirth") or ""
    gender_val = report_data.get("gender") or "Unknown"

    abo_score = float(report_data.get("abo_score", 0.0))
    finishing_score = float(report_data.get("finishing_score", report_data.get("overall_finishing_score", 0.0)))
    andrews_score = float(report_data.get("andrews_score", 0.0))
    root_angulation_score = float(report_data.get("root_angulation_score", 0.0))
    alignment_score = float(report_data.get("alignment_score", report_data.get("arch_symmetry_score", 0.0)))
    confidence_score = float(report_data.get("confidence_score", 0.95))
    midline_val = float(report_data.get("midline_deviation_mm", report_data.get("midlineDiscrepancyMm", 0.0)))
    overjet_val = float(report_data.get("overjet_mm", report_data.get("overjetMm", 0.0)))
    overbite_val = float(report_data.get("overbite_percent", report_data.get("overbitePercent", 0.0)))

    prediction = report_data.get("prediction", "Orthodontic finishing analysis complete.")
    recommendations = report_data.get("recommendations", [])
    metrics = report_data.get("metrics") or report_data.get("details") or {}
    assessment = report_data.get("assessment") or {}
    image_url = report_data.get("image_url") or report_data.get("imagePath") or report_data.get("storage_url") or ""
    view_type = report_data.get("view_type") or report_data.get("viewType") or "opg"
    doctor_name = report_data.get("doctor_name") or report_data.get("doctorName") or "Doctor"
    doctor_email = report_data.get("doctor_email") or ""

    patient_profile = {
        "id": patient_id,
        "name": patient_name,
        "dateOfBirth": dob_val,
        "date_of_birth": dob_val,
        "dob": dob_val,
        "gender": gender_val,
        "phone": report_data.get("phone", ""),
        "email": report_data.get("patient_email", ""),
        "doctorName": doctor_name,
        "doctor_name": doctor_name,
        "doctorId": uid,
        "doctor_id": uid,
        "hospital": "Orthofinix Clinic",
        "diagnosis": "Orthodontic Finishing Assessment",
        "treatmentDate": now_dt.strftime("%d %b %Y"),
        "notes": report_data.get("notes", "AI-generated clinical analysis"),
        "imageUrls": [image_url] if image_url else [],
        "createdAt": now_ms,
        "created_at": now_iso,
    }

    doc_data = {
        "case_id": case_id,
        "caseId": case_id,
        "id": case_id,
        "user_id": uid,
        "uid": uid,
        "doctor_id": uid,
        "doctorId": uid,
        "doctor_email": doctor_email,
        "doctor_name": doctor_name,
        "doctorName": doctor_name,
        "patient_id": patient_id,
        "patientId": patient_id,
        "patient_name": patient_name,
        "patientName": patient_name,
        "dob": dob_val,
        "date_of_birth": dob_val,
        "dateOfBirth": dob_val,
        "gender": gender_val,
        "filename": filename or "",
        "image_url": image_url,
        "imagePath": image_url,
        "storage_url": image_url,
        "view_type": view_type,
        "viewType": view_type,
        "status": "completed",
        "abo_score": abo_score,
        "aboScore": abo_score,
        "finishing_score": finishing_score,
        "overall_finishing_score": finishing_score,
        "andrews_score": andrews_score,
        "andrewsScore": andrews_score,
        "root_angulation_score": root_angulation_score,
        "rootAngulationScore": root_angulation_score,
        "alignment_score": alignment_score,
        "arch_symmetry_score": alignment_score,
        "archSymmetryScore": alignment_score,
        "confidence_score": confidence_score,
        "confidenceScore": confidence_score,
        "midline_deviation_mm": midline_val,
        "midlineDiscrepancyMm": midline_val,
        "overjet_mm": overjet_val,
        "overjetMm": overjet_val,
        "overbite_percent": overbite_val,
        "overbitePercent": overbite_val,
        "prediction": prediction,
        "recommendations": recommendations,
        "metrics": metrics,
        "details": metrics,
        "assessment": assessment,
        "patientProfile": patient_profile,
        "created_at": report_data.get("created_at") or now_iso,
        "createdAt": report_data.get("createdAt") or now_ms,
        "updated_at": now_iso,
        "updatedAt": now_ms,
        "hasReport": True,
    }

    raw_json = json.dumps(doc_data, default=str)
    doc_data["clinicalDataJson"] = raw_json
    doc_data["reportJson"] = raw_json

    safe_data = json.loads(json.dumps(doc_data, default=str))

    try:
        db.collection("analyses").document(case_id).set(safe_data, merge=True)
    except Exception as e:
        print(f"[Firestore] Error saving to 'analyses': {e}")

    try:
        db.collection("cases").document(case_id).set(safe_data, merge=True)
    except Exception as e:
        print(f"[Firestore] Error saving to 'cases': {e}")

    try:
        db.collection("analysis_reports").document(case_id).set(safe_data, merge=True)
    except Exception as e:
        print(f"[Firestore] Error saving to 'analysis_reports': {e}")

    if uid:
        try:
            db.collection("users").document(uid).collection("cases").document(case_id).set(safe_data, merge=True)
            db.collection("users").document(uid).set({
                "last_analysis_at": now_iso,
                "last_active": now_iso,
                "last_case_id": case_id,
                "updated_at": now_iso
            }, merge=True)
        except Exception as e:
            print(f"[Firestore] Error saving to user cases subcollection: {e}")

    try:
        patient_doc = {
            "id": patient_id,
            "name": patient_name,
            "patient_name": patient_name,
            "patientName": patient_name,
            "doctor_id": uid,
            "doctorId": uid,
            "doctor_email": doctor_email,
            "doctor_name": doctor_name,
            "doctorName": doctor_name,
            "date_of_birth": dob_val,
            "dateOfBirth": dob_val,
            "dob": dob_val,
            "gender": gender_val,
            "last_case_id": case_id,
            "lastCaseId": case_id,
            "last_score": finishing_score or abo_score,
            "lastScore": finishing_score or abo_score,
            "last_analysis_at": now_iso,
            "created_at": now_iso,
            "createdAt": now_ms,
            "updated_at": now_iso,
            "updatedAt": now_ms
        }
        db.collection("patients").document(patient_id).set(patient_doc, merge=True)
    except Exception as e:
        print(f"[Firestore] Error saving to 'patients': {e}")

    if image_url:
        try:
            image_id = f"img_{case_id}"
            db.collection("images").document(image_id).set({
                "id": image_id,
                "case_id": case_id,
                "caseId": case_id,
                "user_id": uid,
                "doctor_email": doctor_email,
                "patient_name": patient_name,
                "storage_url": image_url,
                "image_url": image_url,
                "view_type": view_type,
                "uploaded_at": now_iso,
                "createdAt": now_ms
            }, merge=True)
        except Exception as e:
            print(f"[Firestore] Error saving to 'images': {e}")

    return safe_data
