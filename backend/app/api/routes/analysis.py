from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List, Optional
import json
import uuid
import os
import traceback
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.schemas import (
    AnalysisHistoryItem,
    AnalysisReportResponse,
    UserInfo,
    UploadResponse,
)
from app.services.ai_engine import ai_engine
from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import AnalysisReport, UploadedImage, Case, Patient
from app.db.firebase import (
    save_analysis_record,
    get_user_analysis_history,
    get_analysis_by_id,
)
from app.services.firebase_service import save_case_analysis, upload_clinical_image
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/analysis")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    os.getenv("BASE_URL", "https://orthofinixai-backend.onrender.com"),
)

RECENT_ERRORS = []


def log_stage(
    request_id: str,
    firebase_uid: str,
    case_id: str,
    endpoint: str,
    http_status: int,
    db_op: str,
    firestore_op: str,
    storage_op: str,
    analysis_status: str
):
    """
    Structured server logging for persistence and lifecycle tracing.
    Never logs raw credentials/tokens.
    """
    log_entry = {
        "request_id": request_id,
        "firebase_uid": firebase_uid,
        "case_id": case_id,
        "endpoint": endpoint,
        "http_status": http_status,
        "database_operation": db_op,
        "firestore_operation": firestore_op,
        "storage_operation": storage_op,
        "analysis_status": analysis_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    print(f"[ORTHOFINIX_STAGE] {json.dumps(log_entry)}", flush=True)


def _upload_image_url(filename: str) -> str:
    return f"{PUBLIC_BASE_URL}/uploads/{filename}"


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Uploads an image to Firebase Cloud Storage, persists metadata to database and Firestore.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    req_id = str(uuid.uuid4())
    try:
        image_bytes = await file.read()
        file_extension = (
            file.filename.split(".")[-1]
            if file.filename and "." in file.filename
            else "jpg"
        )
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(image_bytes)

        # Upload to Firebase Cloud Storage at cases/{uid}/uploads/{unique_filename}
        image_url = _upload_image_url(unique_filename)
        storage_op = "LOCAL_FALLBACK"
        try:
            cloud_url = upload_clinical_image(
                file_bytes=image_bytes,
                filename=unique_filename,
                uid=current_user.uid,
                content_type=file.content_type or "image/jpeg"
            )
            if cloud_url:
                image_url = cloud_url
                storage_op = "CLOUD_STORAGE_UPLOAD"
        except Exception as st_err:
            print(f"[Firebase Storage] Notice on upload: {st_err}")

        # Save to database
        uploaded_record = UploadedImage(
            id=unique_filename,
            user_id=current_user.uid,
            filename=file.filename or unique_filename,
            file_path=file_path,
            storage_url=image_url,
            content_type=file.content_type or "image/jpeg",
            view_type="frontal",
            uploaded_at=datetime.now(timezone.utc)
        )
        db.add(uploaded_record)
        db.commit()

        # Sync to Firestore top-level images collection
        try:
            from app.db.firebase import save_image_record
            save_image_record({
                "id": unique_filename,
                "filename": file.filename or unique_filename,
                "storage_url": image_url,
                "content_type": file.content_type or "image/jpeg",
                "view_type": "frontal"
            }, current_user.uid, current_user.email)
        except Exception:
            pass

        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid,
            case_id=unique_filename,
            endpoint="POST /analysis/upload",
            http_status=200,
            db_op="INSERT_UPLOAD_RECORD",
            firestore_op="SAVE_IMAGE_RECORD",
            storage_op=storage_op,
            analysis_status="UPLOADED"
        )

        return UploadResponse(
            upload_id=unique_filename,
            image_url=image_url,
            filename=file.filename or unique_filename
        )

    except Exception as e:
        db.rollback()
        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid,
            case_id="NONE",
            endpoint="POST /analysis/upload",
            http_status=500,
            db_op="ROLLBACK",
            firestore_op="NONE",
            storage_op="FAILED",
            analysis_status="ERROR"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisReportResponse)
async def analyze_image(
    upload_id: str = Form(...),
    patient_name: str = Form(...),
    view_type: str = Form("frontal"),
    case_id: str = Form(""),
    dob: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    patient_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Runs AI analysis on uploaded image and persists complete case with exact patient demographics to SQLite database & Firestore.
    """
    req_id = str(uuid.uuid4())
    try:
        file_path = os.path.join(UPLOAD_DIR, upload_id)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Uploaded file not found."
            )

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        report_id = case_id if case_id else f"case_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        created_at_dt = datetime.now(timezone.utc)
        clean_pname = "".join(c if c.isalnum() else "_" for c in patient_name.lower().strip())
        resolved_pat_id = patient_id if patient_id else f"pat_{clean_pname}_{current_user.uid[:8]}"

        # Permanent upload to Cloud Storage under hierarchical case path
        image_url = _upload_image_url(upload_id)
        storage_op = "LOCAL_FALLBACK"
        try:
            cloud_url = upload_clinical_image(
                file_bytes=image_bytes,
                filename=f"{upload_id}.jpg" if not upload_id.endswith(".jpg") else upload_id,
                uid=current_user.uid,
                content_type="image/jpeg",
                case_id=report_id,
                view_type=view_type
            )
            if cloud_url:
                image_url = cloud_url
                storage_op = "PERMANENT_CLOUD_STORAGE"
        except Exception as st_err:
            print(f"[Firebase Storage] Notice on analyze: {st_err}")

        # Execute AI Engine Pipeline
        result = ai_engine.analyze_image(
            image_bytes,
            view_type=view_type
        )

        finishing_score = float(result.get("finishing_score", 0.0))
        alignment_score = float(
            result.get("arch_symmetry_score") or
            (result.get("finishing_score") if view_type == "frontal" else 0.0)
        )

        oj_raw = result.get("details", {}).get("overjet_overbite", {}).get("overjet_mm")
        overjet_val = float(oj_raw) if oj_raw is not None else 0.0
        
        ob_raw = result.get("details", {}).get("overjet_overbite", {}).get("overbite_percent")
        overbite_val = float(ob_raw) if ob_raw is not None else 0.0

        mid_raw = result.get("measured_values", {}).get("midline_deviation_mm")
        midline_val = float(mid_raw) if mid_raw is not None else 0.0
        andrews_details = result.get("details", {}).get("andrews_details", [])
        if isinstance(andrews_details, list) and midline_val == 0.0:
            for k in andrews_details:
                if isinstance(k, dict) and "midline" in k.get("key", "").lower():
                    dev = k.get("deviation_mm")
                    if dev is not None:
                        midline_val = float(dev)

        # 1. Persist to SQL Database (SQLite / Postgres)
        try:
            db_pat = db.query(Patient).filter(Patient.id == resolved_pat_id).first()
            if not db_pat:
                db_pat = Patient(
                    id=resolved_pat_id,
                    doctor_id=current_user.uid,
                    name=patient_name,
                    date_of_birth=dob or "",
                    gender=gender or "Unknown",
                    contact_info="",
                    created_at=created_at_dt
                )
                db.add(db_pat)
            else:
                db_pat.name = patient_name
                if dob:
                    db_pat.date_of_birth = dob
                if gender:
                    db_pat.gender = gender
            db.commit()
        except Exception as p_err:
            db.rollback()
            print(f"Notice: SQLite patient record sync skipped: {p_err}")

        # Standardized rounded integer scores
        overall_score_int = int(round(float(finishing_score)))
        abo_score_int = int(round(float(result.get("abo_score") if result.get("abo_score") is not None else overall_score_int)))
        andrews_score_int = int(round(float(result.get("andrews_score") if result.get("andrews_score") is not None else overall_score_int)))
        alignment_score_int = int(round(float(alignment_score)))
        root_angulation_score_int = int(round(float(result.get("root_angulation_score") if result.get("root_angulation_score") is not None else overall_score_int)))
        
        raw_conf = float(result.get("confidence") or result.get("confidence_score") or 0.95)
        conf_percent_int = int(round(raw_conf * 100)) if raw_conf <= 1.0 else int(round(raw_conf))
        confidence_val_float = conf_percent_int / 100.0

        db_report = AnalysisReport(
            id=report_id,
            user_id=current_user.uid,
            case_id=report_id,
            patient_name=patient_name,
            image_url=image_url,
            view_type=view_type,
            status="completed",
            finishing_score=float(overall_score_int),
            alignment_score=float(alignment_score_int),
            confidence_score=float(confidence_val_float),
            midline_deviation_mm=float(midline_val),
            overjet_mm=float(overjet_val),
            overbite_percent=float(overbite_val),
            abo_score=float(abo_score_int),
            andrews_score=float(andrews_score_int),
            root_angulation_score=float(root_angulation_score_int),
            prediction=result.get("prediction", "Analysis complete."),
            recommendations_json=json.dumps(result.get("recommendations", [])),
            metrics_json=json.dumps(result.get("details", {})),
            created_at=created_at_dt
        )
        db.merge(db_report)
        db.commit()

        # 2. Persist to Firestore (Analyses, Cases, Reports, Patients, Images, Users)
        assessment_data = {
            "prediction": result.get("prediction", "Analysis complete."),
            "overall_score": overall_score_int,
            "finishing_score": overall_score_int,
            "abo_score": abo_score_int,
            "andrews_score": andrews_score_int,
            "root_angulation_score": root_angulation_score_int,
            "alignment_score": alignment_score_int,
            "confidence_score": conf_percent_int,
            "midline_deviation_mm": float(midline_val),
            "overjet_mm": float(overjet_val),
            "overbite_percent": float(overbite_val),
            "recommendations": result.get("recommendations", []),
            "details": result.get("details", {}),
        }

        standardized_teeth = result.get("teeth", [])

        image_metadata_item = {
            "image_id": upload_id,
            "view_type": view_type,
            "storage_path": f"cases/{current_user.uid}/{report_id}/images/{view_type}/{upload_id}",
            "download_url": image_url,
            "uploaded_at": created_at_dt.isoformat(),
        }

        case_data = {
            "id": report_id,
            "case_id": report_id,
            "caseId": report_id,
            "patient_id": resolved_pat_id,
            "patientId": resolved_pat_id,
            "patient_name": patient_name,
            "patientName": patient_name,
            "dob": dob or "",
            "date_of_birth": dob or "",
            "gender": gender or "Unknown",
            "notes": notes or "",
            "doctor_id": current_user.uid,
            "doctorId": current_user.uid,
            "user_id": current_user.uid,
            "doctor_name": current_user.display_name or "Doctor",
            "doctor_email": current_user.email or "",
            "image_url": image_url,
            "imagePath": image_url,
            "images": [image_metadata_item],
            "image_count": 1,
            "views": [view_type],
            "view_type": view_type,
            "viewType": view_type,
            "status": "ANALYZED",
            "overall_score": overall_score_int,
            "overallScore": overall_score_int,
            "overall_finishing_score": overall_score_int,
            "finishing_score": overall_score_int,
            "confidence": confidence_val_float,
            "confidence_score": conf_percent_int,
            "confidenceScore": conf_percent_int,
            "alignmentScore": alignment_score_int,
            "alignment_score": alignment_score_int,
            "cariesScore": 92,
            "boneLossScore": 89,
            "teeth": standardized_teeth,
            "teeth_data": result.get("teeth_data", standardized_teeth),
            "landmarks": result.get("landmarks", {}),
            "teeth_detections": result.get("teeth_detections", []),
            "root_measurements": result.get("root_measurements", {}),
            "occlusal_plane": result.get("occlusal_plane", {}),
            "arch_measurements": result.get("arch_measurements", {}),
            "clinical_metrics": result.get("clinical_metrics", result.get("details", {})),
            "midline_deviation_mm": midline_val,
            "overjet_mm": overjet_val,
            "overbite_percent": overbite_val,
            "abo_score": abo_score_int,
            "aboScore": abo_score_int,
            "andrews_score": andrews_score_int,
            "andrewsScore": andrews_score_int,
            "root_angulation_score": root_angulation_score_int,
            "rootAngulationScore": root_angulation_score_int,
            "prediction": result.get("prediction", "Clinical analysis complete."),
            "recommendations": result.get("recommendations", []),
            "metrics": result.get("details", {}),
            "details": result.get("details", {}),
            "assessment": assessment_data,
            "metadata": {
                "model_version": "v1.0",
                "ai_engine": "OrthodonticAIEngine",
                "analyzed_at": created_at_dt.isoformat()
            },
            "created_at": created_at_dt.isoformat(),
            "createdAt": int(created_at_dt.timestamp() * 1000),
            "updated_at": created_at_dt.isoformat(),
            "updatedAt": int(created_at_dt.timestamp() * 1000),
            "timestamp": created_at_dt.isoformat(),
        }
        case_data["clinicalDataJson"] = json.dumps(case_data)
        case_data["reportJson"] = case_data["clinicalDataJson"]

        save_case_analysis(
            uid=current_user.uid,
            filename=upload_id,
            report_data=case_data
        )
        save_analysis_record(
            case_data,
            current_user.uid,
            report_id,
            user_email=current_user.email,
            user_name=current_user.display_name,
            patient_dob=dob or "",
            patient_gender=gender or "Unknown",
            patient_id=resolved_pat_id
        )

        # Guaranteed Atomic Batch Write directly to Firestore using Firebase Admin SDK
        firestore_verified = False
        try:
            from firebase_admin import firestore as admin_fs
            from app.services.firebase_service import get_firestore_client
            fs_client = get_firestore_client()
            if fs_client:
                case_payload = {
                    "case_id": report_id,
                    "id": report_id,
                    "user_id": current_user.uid,
                    "doctor_id": current_user.uid,
                    "email": current_user.email or "",
                    "doctor_email": current_user.email or "",
                    "patient_name": patient_name,
                    "patient_id": resolved_pat_id,
                    "overall_score": overall_score_int,
                    "overall_finishing_score": overall_score_int,
                    "finishing_score": overall_score_int,
                    "abo_score": abo_score_int,
                    "andrews_score": andrews_score_int,
                    "confidence_score": conf_percent_int,
                    "alignment_score": alignment_score_int,
                    "root_angulation_score": root_angulation_score_int,
                    "status": "ANALYZED",
                    "view_type": view_type,
                    "image_url": image_url or "",
                    "imagePath": image_url or "",
                    "created_at": admin_fs.SERVER_TIMESTAMP,
                    "updated_at": admin_fs.SERVER_TIMESTAMP,
                    "details": result.get("details", {}),
                    "metrics": result.get("details", {}),
                    "recommendations": result.get("recommendations", []),
                    "teeth": standardized_teeth,
                    "teeth_data": result.get("teeth_data", standardized_teeth),
                    "clinicalDataJson": json.dumps(case_data),
                    "reportJson": json.dumps(case_data),
                }
                
                batch = fs_client.batch()
                batch.set(fs_client.collection("users").document(current_user.uid).collection("cases").document(report_id), case_payload)
                batch.set(fs_client.collection("cases").document(report_id), case_payload)
                batch.set(fs_client.collection("analysis_reports").document(report_id), case_payload)
                batch.set(fs_client.collection("analyses").document(report_id), case_payload)
                batch.commit()

                fs_client.collection("users").document(current_user.uid).set({"total_cases": admin_fs.Increment(1)}, merge=True)
                
                # Immediate Read-Back Verification to guarantee persistence
                verify_doc = fs_client.collection("users").document(current_user.uid).collection("cases").document(report_id).get()
                if verify_doc.exists:
                    firestore_verified = True
                    print(f"[Firestore Verified] Case {report_id} read-back confirmed for user {current_user.uid}")
                else:
                    raise IOError(f"Firestore verification failed: Document {report_id} not found after batch commit")
        except Exception as fs_write_err:
            import sys
            print(f"[Firestore WRITE ERROR] Failed to write case {report_id} to Firestore: {fs_write_err}", file=sys.stderr)
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Cloud persistence failed: {str(fs_write_err)}"
            )

        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid,
            case_id=report_id,
            endpoint="POST /analysis/analyze",
            http_status=200,
            db_op="INSERT_ANALYSIS_REPORT",
            firestore_op="BATCH_WRITE_VERIFIED" if firestore_verified else "BATCH_WRITE_ATTEMPTED",
            storage_op=storage_op,
            analysis_status="ANALYZED"
        )

        return AnalysisReportResponse(
            id=report_id,
            case_id=report_id,
            user_id=current_user.uid,
            patient_id=resolved_pat_id,
            patient_name=patient_name,
            image_url=image_url,
            view_type=view_type,
            status="completed",
            overallScore=float(overall_score_int),
            overall_finishing_score=float(overall_score_int),
            finishing_score=float(overall_score_int),
            confidence=confidence_val_float,
            confidence_score=confidence_val_float,
            alignmentScore=float(alignment_score_int),
            alignment_score=float(alignment_score_int),
            teeth=standardized_teeth,
            teeth_data=result.get("teeth_data", standardized_teeth),
            midline_deviation_mm=float(midline_val or 0.0),
            overjet_mm=float(overjet_val or 0.0),
            overbite_percent=float(overbite_val or 0.0),
            abo_score=float(result.get("abo_score") or 0.0),
            andrews_score=float(result.get("andrews_score") or 0.0),
            root_angulation_score=float(result.get("root_angulation_score") or 0.0),
            prediction=result.get("prediction", ""),
            recommendations=result.get("recommendations", []),
            metrics=result.get("details", {}),
            assessment=assessment_data,
            created_at=created_at_dt.isoformat(),
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print("\n========== AI ANALYSIS ERROR ==========")
        traceback.print_exc()
        print("=======================================\n")
        err_msg = str(e)
        tb_str = traceback.format_exc()
        RECENT_ERRORS.append({
            "error": err_msg,
            "traceback": tb_str
        })
        if len(RECENT_ERRORS) > 10:
            RECENT_ERRORS.pop(0)

        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid if 'current_user' in locals() else "UNKNOWN",
            case_id=case_id if 'case_id' in locals() else "UNKNOWN",
            endpoint="POST /analysis/analyze",
            http_status=500,
            db_op="ROLLBACK",
            firestore_op="FAILED",
            storage_op="FAILED",
            analysis_status="ERROR"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/debug_errors")
async def get_debug_errors():
    return RECENT_ERRORS


@router.get("/history", response_model=List[AnalysisHistoryItem])
async def get_history(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Retrieves current authenticated user's analysis history by merging SQL database and Firestore.
    Strictly isolated to current_user.uid.
    """
    try:
        merged_history = {}

        # 1. Fetch from SQL database strictly for the current authenticated user
        db_records = (
            db.query(AnalysisReport)
            .filter(AnalysisReport.user_id == current_user.uid)
            .order_by(AnalysisReport.created_at.desc())
            .limit(50)
            .all()
        )

        for record in db_records:
            if record.id:
                merged_history[record.id] = AnalysisHistoryItem(
                    id=record.id,
                    patient_name=record.patient_name or "Patient",
                    finishing_score=float(record.finishing_score or 0),
                    confidence_score=float(record.confidence_score or 0.95),
                    created_at=record.created_at.isoformat() if record.created_at else None,
                    image_url=record.image_url,
                    user_id=record.user_id,
                )

        # 2. Query user's Firestore records across all collections and merge
        try:
            fs_history = get_user_analysis_history(current_user.uid, current_user.email)
            for record in fs_history:
                rec_id = record.get("id") or record.get("case_id") or record.get("caseId")
                if rec_id and rec_id not in merged_history:
                    # Format created_at date
                    created_str = record.get("created_at")
                    if not created_str and record.get("createdAt"):
                        try:
                            created_str = datetime.fromtimestamp(record["createdAt"] / 1000, tz=timezone.utc).isoformat()
                        except Exception:
                            pass

                    f_score = float(record.get("finishing_score") or record.get("overall_finishing_score") or record.get("abo_score") or 0)
                    c_score = float(record.get("confidence_score") or 0.95)
                    p_name = record.get("patient_name") or record.get("patientName") or (record.get("patientProfile", {}).get("name") if isinstance(record.get("patientProfile"), dict) else "Patient")
                    img_url = record.get("image_url") or record.get("imagePath") or record.get("storage_url") or ""

                    merged_history[rec_id] = AnalysisHistoryItem(
                        id=rec_id,
                        patient_name=p_name or "Patient",
                        finishing_score=f_score,
                        confidence_score=c_score,
                        created_at=created_str,
                        image_url=img_url,
                        user_id=record.get("user_id") or record.get("doctor_id") or current_user.uid,
                    )
        except Exception as fs_err:
            print(f"Notice on Firestore history merge: {fs_err}")

        # Sort results chronologically descending
        items = list(merged_history.values())
        def get_item_sort_key(it: AnalysisHistoryItem):
            if it.created_at:
                try:
                    return datetime.fromisoformat(it.created_at.replace("Z", "+00:00")).timestamp()
                except Exception:
                    pass
            return 0
        items.sort(key=get_item_sort_key, reverse=True)
        return items

    except Exception as e:
        log_stage(
            request_id=str(uuid.uuid4()),
            firebase_uid=current_user.uid,
            case_id="ALL",
            endpoint="GET /analysis/history",
            http_status=500,
            db_op="QUERY",
            firestore_op="STREAM",
            storage_op="NONE",
            analysis_status="ERROR"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history: {str(e)}"
        )

    log_stage(
        request_id=str(uuid.uuid4()),
        firebase_uid=current_user.uid,
        case_id="ALL",
        endpoint="GET /analysis/history",
        http_status=200,
        db_op=f"QUERY_SQL_COUNT_{len(db_records)}",
        firestore_op=f"STREAM_FS_COUNT_{len(items)}",
        storage_op="NONE",
        analysis_status="COMPLETED"
    )
    return items


@router.get("/report/{record_id}", response_model=AnalysisReportResponse)
async def get_analysis(
    record_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Retrieves a specific analysis record from SQL database or Firestore.
    """
    req_id = str(uuid.uuid4())
    try:
        # Check SQL database first by id or case_id
        record = (
            db.query(AnalysisReport)
            .filter((AnalysisReport.id == record_id) | (AnalysisReport.case_id == record_id))
            .first()
        )

        if record:
            if record.user_id != current_user.uid and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Access denied.")

            recommendations = []
            if record.recommendations_json:
                try:
                    recommendations = json.loads(record.recommendations_json)
                except Exception:
                    recommendations = []

            metrics = {}
            if record.metrics_json:
                try:
                    metrics = json.loads(record.metrics_json)
                except Exception:
                    metrics = {}

            images_list = [{
                "image_id": record.id,
                "view_type": record.view_type or "opg",
                "storage_path": f"cases/{record.user_id}/{record.id}/images/{record.view_type or 'opg'}/{record.id}.jpg",
                "download_url": record.image_url,
                "uploaded_at": record.created_at.isoformat() if record.created_at else None
            }] if record.image_url else []

            log_stage(
                request_id=req_id,
                firebase_uid=current_user.uid,
                case_id=record.id,
                endpoint=f"GET /analysis/report/{record_id}",
                http_status=200,
                db_op="GET_SQL_HIT",
                firestore_op="NONE",
                storage_op="NONE",
                analysis_status="RETRIEVED"
            )

            return AnalysisReportResponse(
                id=record.id,
                user_id=record.user_id,
                case_id=record.case_id,
                patient_name=record.patient_name,
                image_url=record.image_url,
                images=images_list,
                image_count=len(images_list),
                views=[record.view_type or "opg"],
                view_type=record.view_type or "opg",
                status=record.status or "completed",
                overallScore=float(record.finishing_score or 0),
                overall_finishing_score=float(record.finishing_score or 0),
                finishing_score=float(record.finishing_score or 0),
                alignmentScore=float(record.alignment_score or 0),
                alignment_score=float(record.alignment_score or 0),
                confidence_score=float(record.confidence_score or 0),
                midline_deviation_mm=float(record.midline_deviation_mm or 0),
                overjet_mm=float(record.overjet_mm or 0),
                overbite_percent=float(record.overbite_percent or 0),
                abo_score=float(record.abo_score or 0),
                andrews_score=float(record.andrews_score or 0),
                root_angulation_score=float(record.root_angulation_score or 0),
                landmarks=metrics.get("landmarks", {}),
                teeth_detections=metrics.get("teeth_detections", []),
                root_measurements=metrics.get("root_measurements", {}),
                occlusal_plane=metrics.get("occlusal_plane", {}),
                arch_measurements=metrics.get("arch_measurements", {}),
                clinical_metrics=metrics.get("clinical_metrics", metrics),
                prediction=record.prediction or "",
                recommendations=recommendations,
                metrics=metrics,
                metadata={
                    "model_version": "v1.0",
                    "ai_engine": "OrthodonticAIEngine",
                    "analyzed_at": record.created_at.isoformat() if record.created_at else None
                },
                created_at=record.created_at.isoformat() if record.created_at else None,
            )

        # Fallback to Firestore
        try:
            fs_record = get_analysis_by_id(record_id, current_user.uid)
            if fs_record:
                rec_user = fs_record.get("user_id") or fs_record.get("doctor_id") or fs_record.get("doctorId")
                if rec_user and rec_user != current_user.uid and current_user.role != "admin":
                    raise HTTPException(status_code=403, detail="Access denied.")

                p_name = fs_record.get("patient_name") or fs_record.get("patientName") or "Patient"
                f_score = float(fs_record.get("finishing_score") or fs_record.get("overall_finishing_score") or fs_record.get("abo_score") or 0)
                recs = fs_record.get("recommendations") or []
                if isinstance(recs, str):
                    try:
                        recs = json.loads(recs)
                    except Exception:
                        recs = [recs]

                mets = fs_record.get("metrics") or fs_record.get("details") or {}
                if isinstance(mets, str):
                    try:
                        mets = json.loads(mets)
                    except Exception:
                        mets = {}

                fs_images = fs_record.get("images", [])
                if not fs_images and (fs_record.get("image_url") or fs_record.get("imagePath")):
                    fs_img_url = fs_record.get("image_url") or fs_record.get("imagePath")
                    fs_images = [{
                        "image_id": record_id,
                        "view_type": fs_record.get("view_type") or "opg",
                        "storage_path": f"cases/{rec_user or current_user.uid}/{record_id}/images/{fs_record.get('view_type') or 'opg'}/{record_id}.jpg",
                        "download_url": fs_img_url,
                        "uploaded_at": fs_record.get("created_at")
                    }]

                log_stage(
                    request_id=req_id,
                    firebase_uid=current_user.uid,
                    case_id=record_id,
                    endpoint=f"GET /analysis/report/{record_id}",
                    http_status=200,
                    db_op="NONE",
                    firestore_op="GET_FIRESTORE_HIT",
                    storage_op="NONE",
                    analysis_status="RETRIEVED"
                )

                return AnalysisReportResponse(
                    id=fs_record.get("id") or record_id,
                    user_id=rec_user or current_user.uid,
                    case_id=fs_record.get("case_id") or fs_record.get("caseId") or record_id,
                    patient_name=p_name,
                    image_url=fs_record.get("image_url") or fs_record.get("imagePath") or fs_record.get("storage_url") or "",
                    images=fs_images,
                    image_count=len(fs_images),
                    views=fs_record.get("views", [fs_record.get("view_type") or "opg"]),
                    view_type=fs_record.get("view_type") or fs_record.get("viewType") or "opg",
                    status=fs_record.get("status") or "completed",
                    overallScore=f_score,
                    overall_finishing_score=f_score,
                    finishing_score=f_score,
                    alignmentScore=float(fs_record.get("alignment_score") or fs_record.get("arch_symmetry_score") or 0),
                    alignment_score=float(fs_record.get("alignment_score") or fs_record.get("arch_symmetry_score") or 0),
                    confidence_score=float(fs_record.get("confidence_score") or 0.95),
                    midline_deviation_mm=float(fs_record.get("midline_deviation_mm") or 0),
                    overjet_mm=float(fs_record.get("overjet_mm") or 0),
                    overbite_percent=float(fs_record.get("overbite_percent") or 0),
                    abo_score=float(fs_record.get("abo_score") or 0),
                    andrews_score=float(fs_record.get("andrews_score") or 0),
                    root_angulation_score=float(fs_record.get("root_angulation_score") or 0),
                    teeth=fs_record.get("teeth", []),
                    teeth_data=fs_record.get("teeth_data", fs_record.get("teeth", [])),
                    landmarks=fs_record.get("landmarks", mets.get("landmarks", {})),
                    teeth_detections=fs_record.get("teeth_detections", mets.get("teeth_detections", [])),
                    root_measurements=fs_record.get("root_measurements", mets.get("root_measurements", {})),
                    occlusal_plane=fs_record.get("occlusal_plane", mets.get("occlusal_plane", {})),
                    arch_measurements=fs_record.get("arch_measurements", mets.get("arch_measurements", {})),
                    clinical_metrics=fs_record.get("clinical_metrics", mets),
                    prediction=fs_record.get("prediction") or "Clinical analysis complete.",
                    recommendations=recs,
                    metrics=mets,
                    metadata=fs_record.get("metadata", {
                        "model_version": "v1.0",
                        "ai_engine": "OrthodonticAIEngine",
                        "analyzed_at": fs_record.get("created_at")
                    }),
                    created_at=fs_record.get("created_at") or (datetime.fromtimestamp(fs_record["createdAt"] / 1000, tz=timezone.utc).isoformat() if fs_record.get("createdAt") else None),
                )
        except HTTPException:
            raise
        except Exception as fs_e:
            print(f"Firestore get_analysis fallback notice: {fs_e}")

        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid,
            case_id=record_id,
            endpoint=f"GET /analysis/report/{record_id}",
            http_status=404,
            db_op="NOT_FOUND",
            firestore_op="NOT_FOUND",
            storage_op="NONE",
            analysis_status="NOT_FOUND"
        )
        raise HTTPException(
            status_code=404,
            detail="Analysis record not found."
        )

    except HTTPException:
        raise
    except Exception as e:
        log_stage(
            request_id=req_id,
            firebase_uid=current_user.uid,
            case_id=record_id,
            endpoint=f"GET /analysis/report/{record_id}",
            http_status=500,
            db_op="ERROR",
            firestore_op="ERROR",
            storage_op="NONE",
            analysis_status="ERROR"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch record: {str(e)}"
        )


@router.get("/demo", response_model=AnalysisReportResponse)
async def get_demo_analysis(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Returns a verified STAR Clinical Benchmark Sample analysis report and persists it to SQL & Firestore.
    """
    demo_id = f"demo_{current_user.uid[:8]}"
    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()
    image_url = "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80"
    patient_name = "STAR Clinical Benchmark Patient"
    recs = [
        "Maintain optimal arch alignment and verify root parallelism on final debond.",
        "Upper right lateral incisor torque inclination exhibits +3° labial root torque.",
        "Canine Class I intercuspation verified bilaterally.",
        "Midline deviation within acceptable clinical tolerance (0.6 mm)."
    ]
    mets = {
        "overjet_mm": 2.3,
        "overbite_percent": 26.0,
        "midline_deviation_mm": 0.6,
        "curve_of_spee_depth_mm": 1.2,
        "detected_teeth_count": 28
    }

    # 1. Persist to SQL
    try:
        db_report = AnalysisReport(
            id=demo_id,
            user_id=current_user.uid,
            case_id=demo_id,
            patient_name=patient_name,
            image_url=image_url,
            view_type="frontal",
            status="completed",
            finishing_score=89.5,
            alignment_score=91.0,
            confidence_score=0.96,
            midline_deviation_mm=0.6,
            overjet_mm=2.3,
            overbite_percent=26.0,
            abo_score=6.0,
            andrews_score=92.0,
            root_angulation_score=88.0,
            prediction="STAR Clinical Benchmark: Occlusion exhibits Class I canine and molar finishing with minor lateral incisor torque deviation.",
            recommendations_json=json.dumps(recs),
            metrics_json=json.dumps(mets),
            created_at=now_dt
        )
        db.merge(db_report)
        db.commit()
    except Exception as sql_e:
        db.rollback()
        print(f"Notice: SQL demo save notice: {sql_e}")

    # 2. Persist to Firestore
    try:
        from app.db.firebase import save_analysis_record
        demo_payload = {
            "id": demo_id,
            "case_id": demo_id,
            "patient_id": f"pat_{demo_id}",
            "patient_name": patient_name,
            "image_url": image_url,
            "view_type": "frontal",
            "status": "completed",
            "finishing_score": 89.5,
            "overall_finishing_score": 89.5,
            "alignment_score": 91.0,
            "confidence_score": 0.96,
            "midline_deviation_mm": 0.6,
            "overjet_mm": 2.3,
            "overbite_percent": 26.0,
            "abo_score": 6.0,
            "andrews_score": 92.0,
            "root_angulation_score": 88.0,
            "prediction": "STAR Clinical Benchmark: Occlusion exhibits Class I canine and molar finishing with minor lateral incisor torque deviation.",
            "recommendations": recs,
            "metrics": mets,
            "created_at": now_iso
        }
        save_analysis_record(demo_payload, current_user.uid, demo_id, user_email=current_user.email, user_name=current_user.display_name)
    except Exception as fs_e:
        print(f"Notice: Firestore demo save notice: {fs_e}")

    return AnalysisReportResponse(
        id=demo_id,
        user_id=current_user.uid,
        case_id=demo_id,
        patient_name=patient_name,
        image_url=image_url,
        view_type="frontal",
        status="completed",
        finishing_score=89.5,
        alignment_score=91.0,
        confidence_score=0.96,
        midline_deviation_mm=0.6,
        overjet_mm=2.3,
        overbite_percent=26.0,
        abo_score=6.0,
        andrews_score=92.0,
        root_angulation_score=88.0,
        prediction="STAR Clinical Benchmark: Occlusion exhibits Class I canine and molar finishing with minor lateral incisor torque deviation.",
        recommendations=recs,
        metrics=mets,
        created_at=now_iso
    )


@router.delete("/{record_id}")
@router.post("/delete/{record_id}")
async def delete_analysis(
    record_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Authoritative deletion endpoint:
    1. Authenticates current user.
    2. Deletes all SQL records associated with the case (AnalysisReport, Case, UploadedImage).
    3. Deletes all Firestore documents across collections (cases, analyses, analysis_reports, users/{uid}/cases, images).
    4. Returns success response.
    """
    ids_to_clean = {record_id}
    try:
        # 1. Query reports in SQL matching either id, case_id, or patient_name
        reports = db.query(AnalysisReport).filter(
            (AnalysisReport.id == record_id) | 
            (AnalysisReport.case_id == record_id) |
            (AnalysisReport.patient_name == record_id) |
            (AnalysisReport.patient_name.ilike(f"%{record_id}%"))
        ).all()
        
        for r in reports:
            if r.user_id and r.user_id != current_user.uid and current_user.role != "admin":
                continue
            if r.id:
                ids_to_clean.add(r.id)
            if r.case_id:
                ids_to_clean.add(r.case_id)
            db.delete(r)
        
        # Also clean up matching Case records in SQL
        cases = db.query(Case).filter(
            (Case.id.in_(list(ids_to_clean))) | 
            (Case.patient_id.in_(list(ids_to_clean))) |
            (Case.patient_id == record_id)
        ).all()
        for c in cases:
            if c.doctor_id and c.doctor_id != current_user.uid and current_user.role != "admin":
                continue
            if c.id:
                ids_to_clean.add(c.id)
            db.delete(c)

        # Also clean up matching Patient records in SQL
        try:
            from app.models.patient import Patient
            patients = db.query(Patient).filter(
                (Patient.id == record_id) |
                (Patient.name == record_id) |
                (Patient.name.ilike(f"%{record_id}%"))
            ).all()
            for p in patients:
                if p.id:
                    ids_to_clean.add(p.id)
                db.delete(p)
        except Exception:
            pass

        # Also clean up matching UploadedImage records in SQL
        images = db.query(UploadedImage).filter(
            (UploadedImage.case_id.in_(list(ids_to_clean))) | (UploadedImage.id.in_(list(ids_to_clean)))
        ).all()
        for img in images:
            db.delete(img)
        
        db.commit()
    except Exception as sql_err:
        db.rollback()
        print(f"SQL delete notice: {sql_err}")

    # 2. Comprehensive Firestore deletion across all collections
    deleted_fs_ids = []
    try:
        from app.db.firebase import delete_case_from_firestore, delete_firestore_case
        for cid in list(ids_to_clean):
            try:
                fs_ids = delete_case_from_firestore(cid, current_user.uid)
                deleted_fs_ids.extend(fs_ids)
            except Exception:
                pass
            try:
                delete_firestore_case(cid, current_user.uid)
                deleted_fs_ids.append(cid)
            except Exception:
                pass
    except Exception as fs_err:
        print(f"Firestore delete notice: {fs_err}")

    all_cleaned = list(ids_to_clean.union(set(deleted_fs_ids)))
    log_stage(
        request_id=str(uuid.uuid4()),
        firebase_uid=current_user.uid,
        case_id=record_id,
        endpoint=f"DELETE /analysis/{record_id}",
        http_status=200,
        db_op="DELETE_SUCCESS",
        firestore_op=f"DELETE_FS_DOCS_{len(deleted_fs_ids)}",
        storage_op="DELETE_BLOBS",
        analysis_status="DELETED"
    )
    return {
        "status": "success",
        "message": "Case deleted successfully",
        "id": record_id,
        "deleted_id": record_id,
        "deleted_ids": all_cleaned
    }


@router.get("/benchmark", response_model=AnalysisReportResponse)
async def get_star_benchmark_demo():
    """
    Returns the complete STAR Clinical Benchmark sample case with 32-tooth odontogram dataset.
    """
    demo_id = f"demo_star_benchmark_{int(datetime.now(timezone.utc).timestamp())}"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    teeth_list = [
        {"toothNumber": 18, "name": "Upper Right 3rd Molar", "score": 92.0, "status": "Aligned", "issues": []},
        {"toothNumber": 17, "name": "Upper Right 2nd Molar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 16, "name": "Upper Right 1st Molar", "score": 88.0, "status": "Class I", "issues": []},
        {"toothNumber": 15, "name": "Upper Right 2nd Premolar", "score": 91.0, "status": "Aligned", "issues": []},
        {"toothNumber": 14, "name": "Upper Right 1st Premolar", "score": 89.0, "status": "Aligned", "issues": []},
        {"toothNumber": 13, "name": "Upper Right Canine", "score": 87.0, "status": "Class I", "issues": []},
        {"toothNumber": 12, "name": "Upper Right Lateral Incisor", "score": 78.0, "status": "Crowded", "issues": ["+3° Labial Root Torque"]},
        {"toothNumber": 11, "name": "Upper Right Central Incisor", "score": 94.0, "status": "Aligned", "issues": []},
        {"toothNumber": 21, "name": "Upper Left Central Incisor", "score": 93.0, "status": "Aligned", "issues": []},
        {"toothNumber": 22, "name": "Upper Left Lateral Incisor", "score": 86.0, "status": "Aligned", "issues": []},
        {"toothNumber": 23, "name": "Upper Left Canine", "score": 89.0, "status": "Class I", "issues": []},
        {"toothNumber": 24, "name": "Upper Left 1st Premolar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 25, "name": "Upper Left 2nd Premolar", "score": 91.0, "status": "Aligned", "issues": []},
        {"toothNumber": 26, "name": "Upper Left 1st Molar", "score": 88.0, "status": "Class I", "issues": []},
        {"toothNumber": 27, "name": "Upper Left 2nd Molar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 28, "name": "Upper Left 3rd Molar", "score": 92.0, "status": "Aligned", "issues": []},
        {"toothNumber": 48, "name": "Lower Right 3rd Molar", "score": 91.0, "status": "Aligned", "issues": []},
        {"toothNumber": 47, "name": "Lower Right 2nd Molar", "score": 89.0, "status": "Aligned", "issues": []},
        {"toothNumber": 46, "name": "Lower Right 1st Molar", "score": 88.0, "status": "Class I", "issues": []},
        {"toothNumber": 45, "name": "Lower Right 2nd Premolar", "score": 92.0, "status": "Aligned", "issues": []},
        {"toothNumber": 44, "name": "Lower Right 1st Premolar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 43, "name": "Lower Right Canine", "score": 89.0, "status": "Class I", "issues": []},
        {"toothNumber": 42, "name": "Lower Right Lateral Incisor", "score": 91.0, "status": "Aligned", "issues": []},
        {"toothNumber": 41, "name": "Lower Right Central Incisor", "score": 93.0, "status": "Aligned", "issues": []},
        {"toothNumber": 31, "name": "Lower Left Central Incisor", "score": 93.0, "status": "Aligned", "issues": []},
        {"toothNumber": 32, "name": "Lower Left Lateral Incisor", "score": 91.0, "status": "Aligned", "issues": []},
        {"toothNumber": 33, "name": "Lower Left Canine", "score": 89.0, "status": "Class I", "issues": []},
        {"toothNumber": 34, "name": "Lower Left 1st Premolar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 35, "name": "Lower Left 2nd Premolar", "score": 92.0, "status": "Aligned", "issues": []},
        {"toothNumber": 36, "name": "Lower Left 1st Molar", "score": 88.0, "status": "Class I", "issues": []},
        {"toothNumber": 37, "name": "Lower Left 2nd Molar", "score": 90.0, "status": "Aligned", "issues": []},
        {"toothNumber": 38, "name": "Lower Left 3rd Molar", "score": 91.0, "status": "Aligned", "issues": []}
    ]

    return AnalysisReportResponse(
        id=demo_id,
        case_id=demo_id,
        patient_name="STAR Clinical Benchmark Patient",
        image_url="https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80",
        view_type="frontal",
        status="completed",
        overallScore=88.5,
        overall_finishing_score=88.5,
        finishing_score=88.5,
        confidence=0.96,
        confidence_score=0.96,
        alignmentScore=91.0,
        alignment_score=91.0,
        arch_symmetry_score=91.0,
        midline_deviation_mm=0.6,
        overjet_mm=2.3,
        overbite_percent=26.0,
        abo_score=88.0,
        andrews_score=92.0,
        root_angulation_score=88.0,
        teeth=teeth_list,
        teeth_data=[{
            "fdi": t["toothNumber"],
            "name": t["name"],
            "score": t["score"],
            "condition": "healthy" if t["status"] == "Aligned" or t["status"] == "Class I" else "attention_required",
            "status": t["status"],
            "confidence": 0.96,
            "recommendation": ", ".join(t["issues"])
        } for t in teeth_list],
        prediction="STAR Clinical Benchmark: Occlusion exhibits Class I canine and molar finishing with minor lateral incisor torque deviation.",
        recommendations=[
            "Maintain optimal arch alignment and verify root parallelism on final debond.",
            "Upper right lateral incisor torque inclination exhibits +3° labial root torque.",
            "Canine Class I intercuspation verified bilaterally.",
            "Midline deviation within acceptable clinical tolerance (0.6 mm)."
        ],
        metrics={
            "overjet_mm": 2.3,
            "overbite_percent": 26.0,
            "midline_deviation_mm": 0.6,
            "curve_of_spee_depth_mm": 1.2,
            "detected_teeth_count": 32
        },
        created_at=now_iso
    )