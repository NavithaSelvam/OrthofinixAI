import os
import uuid
import json
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from app.core.config import settings

def init_firebase():
    if not firebase_admin._apps:
        try:
            cred = None
            firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH", getattr(settings, "FIREBASE_CREDENTIALS_PATH", None))
            possible_paths = [
                firebase_path,
                "firebase-adminsdk.json.json",
                "firebase-adminsdk.json",
                os.path.join(os.path.dirname(__file__), "..", "..", "firebase-adminsdk.json.json"),
                os.path.join(os.path.dirname(__file__), "..", "..", "firebase-adminsdk.json"),
                os.path.join(os.getcwd(), "firebase-adminsdk.json.json"),
                os.path.join(os.getcwd(), "firebase-adminsdk.json"),
            ]
            for p in possible_paths:
                if p and os.path.exists(p):
                    try:
                        cred = credentials.Certificate(p)
                        print(f"Loaded Firebase credentials from: {p}")
                        break
                    except Exception as err:
                        print(f"Failed to load certificate from {p}: {err}")

            bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET", "orthofinixai.firebasestorage.app")

            if cred:
                firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})
            else:
                firebase_admin.initialize_app(options={'storageBucket': bucket_name})
        except Exception as e:
            print(f"Firebase initialization failed: {e}")

def get_db():
    return firestore.client()

get_firestore_client = get_db

def get_auth():
    return auth

def save_user_profile(user_id: str, email: str, display_name: str = "Doctor", role: str = "doctor", provider: str = "password") -> dict:
    """
    Saves or updates user profile document in Firestore users/{user_id} and records activity.
    Ensures the user document is completely populated in Firebase Console.
    """
    if not user_id:
        return {}
    try:
        db = get_db()
        now_iso = datetime.now(timezone.utc).isoformat()
        user_doc = {
            "uid": user_id,
            "email": email or "",
            "display_name": display_name or "Doctor",
            "role": role or "doctor",
            "provider": provider or "password",
            "last_active": now_iso,
            "last_login": now_iso,
            "updated_at": now_iso,
        }
        # 1. Update root users collection
        db.collection("users").document(user_id).set(user_doc, merge=True)
        return user_doc
    except Exception as e:
        print(f"Firestore user profile save error: {e}")
        return {}

def log_user_login(user_id: str, email: str, display_name: str = "Doctor", event: str = "login", details: dict = None) -> None:
    """
    Logs user authentication and action event to login_logs and activity_logs root collections in Firestore.
    """
    try:
        db = get_db()
        now_iso = datetime.now(timezone.utc).isoformat()
        log_id = str(uuid.uuid4())
        log_entry = {
            "id": log_id,
            "uid": user_id or "",
            "email": email or "",
            "display_name": display_name or "Doctor",
            "event": event,
            "timestamp": now_iso,
            "details": details or {}
        }
        
        # Write to login_logs for login/register events
        if event in ("login", "register", "token_verified"):
            db.collection("login_logs").document(log_id).set(log_entry)
            
        # Write to activity_logs
        db.collection("activity_logs").document(log_id).set(log_entry)
    except Exception as e:
        print(f"Firestore activity log error: {e}")

def save_analysis_record(
    data: dict, 
    user_id: str, 
    provided_case_id: str = "", 
    user_email: str = "", 
    user_name: str = "",
    patient_dob: str = "",
    patient_gender: str = "",
    patient_id: str = ""
) -> dict:
    """
    Saves complete analysis report to:
    1. cases/{record_id} (top-level collection)
    2. analysis_reports/{record_id} (top-level collection)
    3. analyses/{record_id} (top-level collection)
    4. users/{user_id}/cases/{record_id} (subcollection)
    5. patients/{patient_id} (top-level collection)
    6. images/{image_id} (top-level collection if image present)
    7. updates users/{user_id} profile with last_analysis_at and total_cases
    8. logs to activity_logs
    """
    db = get_db()
    record_id = provided_case_id if provided_case_id else str(uuid.uuid4())
    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()
    now_ms = int(now_dt.timestamp() * 1000)
    
    patient_name = data.get("patient_name") or data.get("patientName") or "Patient"
    clean_pname = "".join(c if c.isalnum() else "_" for c in patient_name.lower().strip())
    pat_id = patient_id if patient_id else (f"pat_{clean_pname}_{user_id[:8]}" if user_id else f"pat_{clean_pname}_{record_id[:8]}")

    dob_val = patient_dob or data.get("dob") or data.get("date_of_birth") or data.get("dateOfBirth") or ""
    gender_val = patient_gender or data.get("gender") or "Unknown"

    raw_finishing = float(data.get("overall_score") or data.get("overallScore") or data.get("finishing_score") or data.get("overall_finishing_score") or 0.0)
    finishing_score_int = int(round(raw_finishing))
    abo_score_int = int(round(float(data.get("abo_score") or data.get("aboScore") or finishing_score_int)))
    andrews_score_int = int(round(float(data.get("andrews_score") or data.get("andrewsScore") or finishing_score_int)))
    root_angulation_score_int = int(round(float(data.get("root_angulation_score") or data.get("rootAngulationScore") or finishing_score_int)))
    alignment_score_int = int(round(float(data.get("alignment_score") or data.get("alignmentScore") or data.get("arch_symmetry_score") or finishing_score_int)))
    
    raw_conf = float(data.get("confidence_score") or data.get("confidenceScore") or data.get("confidence") or 0.95)
    conf_int = int(round(raw_conf * 100)) if raw_conf <= 1.0 else int(round(raw_conf))
    conf_float = conf_int / 100.0
    
    midline_val = float(data.get("midline_deviation_mm", data.get("midlineDiscrepancyMm", 0.0)))
    overjet_val = float(data.get("overjet_mm", data.get("overjetMm", 0.0)))
    overbite_val = float(data.get("overbite_percent", data.get("overbitePercent", 0.0)))
    image_url = data.get("image_url") or data.get("imagePath") or data.get("storage_url") or ""
    view_type = data.get("view_type") or data.get("viewType") or "opg"
    prediction = data.get("prediction", "Orthodontic finishing analysis complete.")
    recommendations = data.get("recommendations", [])
    metrics = data.get("metrics") or data.get("details") or {}
    assessment = data.get("assessment") or {}

    patient_profile = {
        "id": pat_id,
        "name": patient_name,
        "dateOfBirth": dob_val,
        "date_of_birth": dob_val,
        "dob": dob_val,
        "gender": gender_val,
        "phone": data.get("phone", ""),
        "email": data.get("patient_email", ""),
        "doctorName": user_name or "Doctor",
        "doctor_name": user_name or "Doctor",
        "doctorId": user_id,
        "doctor_id": user_id,
        "hospital": "Orthofinix Clinic",
        "diagnosis": "Orthodontic Finishing Assessment",
        "treatmentDate": now_dt.strftime("%d %b %Y"),
        "notes": data.get("notes", "AI-generated clinical analysis"),
        "imageUrls": [image_url] if image_url else [],
        "createdAt": now_ms,
        "created_at": now_iso,
    }

    doc_payload = {
        "id": record_id,
        "case_id": record_id,
        "caseId": record_id,
        "patient_id": pat_id,
        "patientId": pat_id,
        "patient_name": patient_name,
        "patientName": patient_name,
        "dob": dob_val,
        "date_of_birth": dob_val,
        "dateOfBirth": dob_val,
        "gender": gender_val,
        "doctor_id": user_id,
        "doctorId": user_id,
        "doctor_email": user_email,
        "doctor_name": user_name or "Doctor",
        "doctorName": user_name or "Doctor",
        "image_url": image_url,
        "imagePath": image_url,
        "storage_url": image_url,
        "images": data.get("images", [{
            "image_id": record_id,
            "view_type": view_type,
            "storage_path": f"cases/{user_id}/{record_id}/images/{view_type}/{record_id}.jpg",
            "download_url": image_url,
            "uploaded_at": now_iso
        }] if image_url else []),
        "image_count": data.get("image_count", 1 if image_url else 0),
        "views": data.get("views", [view_type] if view_type else []),
        "view_type": view_type,
        "viewType": view_type,
        "status": data.get("status", "ANALYZED"),
        "overall_score": finishing_score_int,
        "overallScore": finishing_score_int,
        "overall_finishing_score": finishing_score_int,
        "finishing_score": finishing_score_int,
        "alignmentScore": alignment_score_int,
        "alignment_score": alignment_score_int,
        "arch_symmetry_score": alignment_score_int,
        "archSymmetryScore": alignment_score_int,
        "confidence_score": conf_int,
        "confidenceScore": conf_int,
        "confidence": conf_float,
        "midline_deviation_mm": midline_val,
        "midlineDiscrepancyMm": midline_val,
        "overjet_mm": overjet_val,
        "overjetMm": overjet_val,
        "overbite_percent": overbite_val,
        "overbitePercent": overbite_val,
        "abo_score": abo_score_int,
        "aboScore": abo_score_int,
        "andrews_score": andrews_score_int,
        "andrewsScore": andrews_score_int,
        "root_angulation_score": root_angulation_score_int,
        "rootAngulationScore": root_angulation_score_int,
        "teeth": data.get("teeth", []),
        "teeth_data": data.get("teeth_data", data.get("teeth", [])),
        "landmarks": data.get("landmarks", {}),
        "teeth_detections": data.get("teeth_detections", []),
        "root_measurements": data.get("root_measurements", {}),
        "occlusal_plane": data.get("occlusal_plane", {}),
        "arch_measurements": data.get("arch_measurements", {}),
        "clinical_metrics": data.get("clinical_metrics", metrics),
        "prediction": prediction,
        "recommendations": recommendations,
        "metrics": metrics,
        "details": metrics,
        "assessment": assessment,
        "metadata": data.get("metadata", {
            "model_version": "v1.0",
            "ai_engine": "OrthodonticAIEngine",
            "analyzed_at": now_iso
        }),
        "patientProfile": patient_profile,
        "hasReport": True,
        "created_at": data.get("created_at") or now_iso,
        "createdAt": data.get("createdAt") or now_ms,
        "updated_at": now_iso,
        "updatedAt": now_ms,
    }

    raw_json = json.dumps(doc_payload, default=str)
    doc_payload["clinicalDataJson"] = raw_json
    doc_payload["reportJson"] = raw_json

    safe_data = json.loads(json.dumps(doc_payload, default=str))

    # 1. Update user profile document in Firestore
    if user_id:
        try:
            db.collection("users").document(user_id).set({
                "uid": user_id,
                "email": user_email,
                "display_name": user_name or "Doctor",
                "last_active": now_iso,
                "last_analysis_at": now_iso,
                "last_case_id": record_id,
                "updated_at": now_iso
            }, merge=True)
        except Exception as err:
            print(f"Firestore user update error: {err}")

    # 2. Save into TOP-LEVEL collection cases/{record_id}
    try:
        db.collection("cases").document(record_id).set(safe_data, merge=True)
    except Exception as err:
        print(f"Firestore top-level cases save error: {err}")

    # 3. Save into TOP-LEVEL collection analysis_reports/{record_id}
    try:
        db.collection("analysis_reports").document(record_id).set(safe_data, merge=True)
    except Exception as err:
        print(f"Firestore top-level analysis_reports save error: {err}")

    # 4. Save into TOP-LEVEL collection analyses/{record_id}
    try:
        db.collection("analyses").document(record_id).set(safe_data, merge=True)
    except Exception as err:
        print(f"Firestore top-level analyses save error: {err}")

    # 5. Save into subcollection users/{user_id}/cases/{record_id}
    if user_id:
        try:
            db.collection("users").document(user_id).collection("cases").document(record_id).set(safe_data, merge=True)
            db.collection("users").document(user_id).collection("analyses").document(record_id).set(safe_data, merge=True)
            # Update user's total_cases count
            user_cases = list(db.collection("users").document(user_id).collection("cases").stream())
            db.collection("users").document(user_id).set({
                "total_cases": len(user_cases),
                "last_active": now_iso,
                "last_analysis_at": now_iso,
                "last_case_id": record_id,
                "updated_at": now_iso
            }, merge=True)
        except Exception as err:
            print(f"Firestore subcollection cases save error: {err}")

    # 6. Save into TOP-LEVEL collection patients/{pat_id}
    try:
        patient_doc = {
            "id": pat_id,
            "name": patient_name,
            "patient_name": patient_name,
            "patientName": patient_name,
            "doctor_id": user_id,
            "doctorId": user_id,
            "doctor_email": user_email,
            "doctor_name": user_name or "Doctor",
            "doctorName": user_name or "Doctor",
            "date_of_birth": dob_val,
            "dateOfBirth": dob_val,
            "dob": dob_val,
            "gender": gender_val,
            "last_case_id": record_id,
            "lastCaseId": record_id,
            "last_score": finishing_score_int or abo_score_int,
            "lastScore": finishing_score_int or abo_score_int,
            "last_analysis_at": now_iso,
            "created_at": now_iso,
            "createdAt": now_ms,
            "updated_at": now_iso,
            "updatedAt": now_ms
        }
        db.collection("patients").document(pat_id).set(patient_doc, merge=True)
    except Exception as err:
        print(f"Firestore patient record save error: {err}")

    # 7. Save into TOP-LEVEL collection images/{image_id} if image_url exists
    if image_url:
        try:
            image_id = f"img_{record_id}"
            db.collection("images").document(image_id).set({
                "id": image_id,
                "case_id": record_id,
                "caseId": record_id,
                "user_id": user_id,
                "doctor_email": user_email,
                "patient_name": patient_name,
                "storage_url": image_url,
                "image_url": image_url,
                "view_type": view_type,
                "uploaded_at": now_iso,
                "createdAt": now_ms
            }, merge=True)
        except Exception as err:
            print(f"Firestore image save error: {err}")

    # 8. Log activity
    try:
        log_user_login(
            user_id, 
            user_email, 
            user_name, 
            event="analysis_created", 
            details={"case_id": record_id, "patient_name": patient_name, "score": finishing_score}
        )
    except Exception:
        pass

    return safe_data

def save_image_record(image_data: dict, user_id: str, user_email: str = "") -> dict:
    """
    Saves uploaded image metadata into top-level images collection in Firestore.
    """
    try:
        db = get_db()
        image_id = image_data.get("id") or str(uuid.uuid4())
        image_data["id"] = image_id
        image_data["user_id"] = user_id
        image_data["doctor_email"] = user_email
        image_data["uploaded_at"] = image_data.get("uploaded_at") or datetime.now(timezone.utc).isoformat()
        
        safe_data = json.loads(json.dumps(image_data))
        db.collection("images").document(image_id).set(safe_data, merge=True)
        return safe_data
    except Exception as e:
        print(f"Firestore image record save error: {e}")
        return image_data

def get_user_analysis_history(user_id: str, email: str = "") -> list:
    if not user_id or user_id == "anonymous":
        return []
    case_map = {}
    try:
        db = get_db()
    except Exception as e:
        print(f"Firestore get_db error: {e}")
        return []

    # 1. Query subcollection users/{user_id}/cases
    try:
        docs = db.collection("users").document(user_id).collection("cases").stream()
        for doc in docs:
            d = doc.to_dict()
            doc_id = d.get("id") or d.get("case_id") or d.get("caseId") or doc.id
            if doc_id:
                case_map[doc_id] = d
    except Exception as e:
        print(f"Firestore users subcollection stream notice: {e}")

    # 2. Query root collections across user field variations
    colls = ["cases", "analysis_reports", "analyses"]
    fields = ["doctor_id", "doctorId", "user_id", "uid"]
    for coll_name in colls:
        for field in fields:
            try:
                docs = db.collection(coll_name).where(field, "==", user_id).limit(50).stream()
                for doc in docs:
                    d = doc.to_dict()
                    doc_id = d.get("id") or d.get("case_id") or d.get("caseId") or doc.id
                    if doc_id and doc_id not in case_map:
                        case_map[doc_id] = d
            except Exception:
                pass

        if email:
            for em_field in ["doctor_email", "email"]:
                try:
                    docs = db.collection(coll_name).where(em_field, "==", email).limit(50).stream()
                    for doc in docs:
                        d = doc.to_dict()
                        doc_id = d.get("id") or d.get("case_id") or d.get("caseId") or doc.id
                        if doc_id and doc_id not in case_map:
                            case_map[doc_id] = d
                except Exception:
                    pass

    results = list(case_map.values())
    
    # Sort chronologically descending
    def get_sort_key(item):
        ts = item.get("createdAt") or item.get("created_at") or 0
        if isinstance(ts, (int, float)):
            return ts
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000
            except Exception:
                pass
        return 0

    results.sort(key=get_sort_key, reverse=True)
    return results

def delete_case_from_firestore(case_id: str, user_id: str = "") -> list:
    """
    Permanently deletes a case and all its related documents across all Firestore collections:
    - users/{user_id}/cases
    - cases
    - analysis_reports
    - analyses
    - images
    Returns list of deleted document IDs.
    """
    if not case_id:
        return []
    deleted_ids = set([case_id])
    try:
        db = get_db()
    except Exception as e:
        print(f"Firestore get_db error on delete: {e}")
        return list(deleted_ids)

    # 1. Delete from user subcollection users/{user_id}/cases
    if user_id and user_id != "anonymous":
        try:
            user_cases = db.collection("users").document(user_id).collection("cases").stream()
            for doc in user_cases:
                d = doc.to_dict()
                d_id = d.get("id", "")
                d_case_id = d.get("case_id", "") or d.get("caseId", "")
                if doc.id == case_id or d_id == case_id or d_case_id == case_id:
                    deleted_ids.add(doc.id)
                    if d_id:
                        deleted_ids.add(d_id)
                    if d_case_id:
                        deleted_ids.add(d_case_id)
                    doc.reference.delete()
        except Exception as e:
            print(f"Firestore user subcollection delete notice: {e}")

    # 2. Direct document delete across candidate IDs with ownership verification
    all_target_ids = list(deleted_ids)
    for cid in all_target_ids:
        for coll_name in ["cases", "analysis_reports", "analyses"]:
            try:
                doc_snap = db.collection(coll_name).document(cid).get()
                if doc_snap.exists:
                    d = doc_snap.to_dict()
                    d_user = d.get("user_id") or d.get("doctor_id") or d.get("doctorId")
                    if not user_id or not d_user or d_user == user_id:
                        db.collection(coll_name).document(cid).delete()
            except Exception:
                pass
        try:
            img_snap = db.collection("images").document(f"img_{cid}").get()
            if img_snap.exists:
                d_user = img_snap.to_dict().get("user_id") or img_snap.to_dict().get("doctor_id")
                if not user_id or not d_user or d_user == user_id:
                    db.collection("images").document(f"img_{cid}").delete()
        except Exception:
            pass
        if user_id and user_id != "anonymous":
            try:
                db.collection("users").document(user_id).collection("cases").document(cid).delete()
                db.collection("users").document(user_id).collection("analyses").document(cid).delete()
            except Exception:
                pass

    # 3. Query root 'cases' matching case_id, caseId, or id
    try:
        cases_docs = db.collection("cases").stream()
        for doc in cases_docs:
            d = doc.to_dict()
            d_id = d.get("id", "")
            d_case_id = d.get("case_id", "") or d.get("caseId", "")
            d_user = d.get("user_id", "") or d.get("doctor_id", "") or d.get("doctorId", "")
            if doc.id in deleted_ids or d_id in deleted_ids or d_case_id in deleted_ids:
                if not user_id or d_user == user_id or not d_user:
                    deleted_ids.add(doc.id)
                    doc.reference.delete()
    except Exception as e:
        print(f"Firestore root cases query delete notice: {e}")

    # 4. Query root 'analysis_reports' matching ID
    try:
        reports_docs = db.collection("analysis_reports").stream()
        for doc in reports_docs:
            d = doc.to_dict()
            d_id = d.get("id", "")
            d_case_id = d.get("case_id", "") or d.get("caseId", "")
            d_user = d.get("user_id", "") or d.get("doctor_id", "")
            if doc.id in deleted_ids or d_id in deleted_ids or d_case_id in deleted_ids:
                if not user_id or d_user == user_id or not d_user:
                    deleted_ids.add(doc.id)
                    doc.reference.delete()
    except Exception as e:
        print(f"Firestore root analysis_reports query delete notice: {e}")

    # 5. Query root 'analyses' matching ID
    try:
        analyses_docs = db.collection("analyses").stream()
        for doc in analyses_docs:
            d = doc.to_dict()
            d_id = d.get("id", "")
            d_case_id = d.get("case_id", "") or d.get("caseId", "")
            d_user = d.get("user_id", "") or d.get("doctor_id", "")
            if doc.id in deleted_ids or d_id in deleted_ids or d_case_id in deleted_ids:
                if not user_id or d_user == user_id or not d_user:
                    deleted_ids.add(doc.id)
                    doc.reference.delete()
    except Exception as e:
        print(f"Notice cleaning analyses: {e}")

    # 6. Delete Cloud Storage image blobs for the case
    if user_id and user_id != "anonymous":
        try:
            from firebase_admin import storage
            for b_name in [os.getenv("FIREBASE_STORAGE_BUCKET"), "orthofinixai.firebasestorage.app", "orthofinixai.appspot.com"]:
                if not b_name:
                    continue
                try:
                    bucket = storage.bucket(b_name)
                    for cid in all_target_ids:
                        prefix = f"cases/{user_id}/{cid}"
                        blobs = bucket.list_blobs(prefix=prefix)
                        for blob in blobs:
                            try:
                                blob.delete()
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as st_err:
            print(f"Cloud Storage delete notice: {st_err}")

    # 7. Update user total_cases count
    if user_id and user_id != "anonymous":
        try:
            remaining_cases = list(db.collection("users").document(user_id).collection("cases").stream())
            db.collection("users").document(user_id).set({
                "total_cases": len(remaining_cases),
                "last_active": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }, merge=True)
        except Exception as e:
            print(f"User total_cases update after deletion notice: {e}")

    return list(deleted_ids)

def upload_image_to_storage(file_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """
    Save image file to local disk and return a servable URL.
    """
    try:
        os.makedirs("uploads", exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join("uploads", unique_filename)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        base_url = os.getenv("PUBLIC_BASE_URL", "https://orthofinixai-backend.onrender.com")
        return f"{base_url}/uploads/{unique_filename}"
    except Exception as e:
        print(f"Local Storage Write Error: {e}")
        raise ValueError(f"Failed to write image to storage: {e}")

def get_analysis_by_id(record_id: str, user_id: str = "") -> dict:
    try:
        db = get_db()
    except Exception:
        return None

    if not record_id:
        return None

    # 1. Check user subcollection if user_id is provided
    if user_id and user_id != "anonymous":
        try:
            doc = db.collection("users").document(user_id).collection("cases").document(record_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass

    # 2. Check top-level collections by document ID
    for coll_name in ["cases", "analysis_reports", "analyses"]:
        try:
            doc = db.collection(coll_name).document(record_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass

    # 3. Check collections by field queries safely
    fields = ["case_id", "caseId", "patient_id", "patientId"]
    for coll_name in ["cases", "analysis_reports", "analyses"]:
        for field in fields:
            try:
                docs = db.collection(coll_name).where(field, "==", record_id).limit(1).stream()
                for d in docs:
                    return d.to_dict()
            except Exception:
                pass

    return None


def delete_firestore_case(case_id: str, user_id: str = "") -> bool:
    """
    Cascade deletes a case across all Firestore locations and user subcollections.
    """
    try:
        db = get_db()
    except Exception:
        return False

    if not case_id:
        return False

    success = False

    # 1. Delete from user subcollection if user_id is provided
    if user_id and user_id != "anonymous":
        try:
            db.collection("users").document(user_id).collection("cases").document(case_id).delete()
            success = True
        except Exception as e:
            print(f"Notice deleting user subcollection case: {e}")

    # 2. Delete from top-level collections by document ID
    for coll_name in ["cases", "analysis_reports", "analyses", "images"]:
        try:
            db.collection(coll_name).document(case_id).delete()
            success = True
        except Exception as e:
            print(f"Notice deleting {coll_name}/{case_id}: {e}")

    # 3. Query and delete any matching documents by case_id / id
    fields = ["case_id", "caseId", "id"]
    for coll_name in ["cases", "analysis_reports", "analyses", "images"]:
        for field in fields:
            try:
                docs = db.collection(coll_name).where(field, "==", case_id).stream()
                for doc in docs:
                    doc.reference.delete()
                    success = True
            except Exception:
                pass

    return success


def delete_firestore_patient(patient_id: str, user_id: str = "") -> bool:
    """
    Cascade deletes a patient and all associated cases from Firestore.
    """
    try:
        db = get_db()
    except Exception:
        return False

    if not patient_id:
        return False

    success = False

    # 1. Delete root patients document
    try:
        db.collection("patients").document(patient_id).delete()
        success = True
    except Exception as e:
        print(f"Notice deleting patients/{patient_id}: {e}")

    # 2. Query and delete from patients collection by field
    for field in ["id", "patient_id", "patientId"]:
        try:
            docs = db.collection("patients").where(field, "==", patient_id).stream()
            for doc in docs:
                doc.reference.delete()
                success = True
        except Exception:
            pass

    # 3. Cascade delete any cases associated with this patient
    for field in ["patient_id", "patientId"]:
        for coll_name in ["cases", "analysis_reports", "analyses"]:
            try:
                docs = db.collection(coll_name).where(field, "==", patient_id).stream()
                for doc in docs:
                    delete_firestore_case(doc.id, user_id)
            except Exception:
                pass

    return success

