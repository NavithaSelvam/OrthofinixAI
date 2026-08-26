from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from datetime import datetime, timezone
import uuid
import os
from sqlalchemy.orm import Session

from app.models.schemas import CaseCreate, CaseResponse, UserInfo
from app.api.dependencies import get_current_user
from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import Case, Patient, UploadedImage
from app.db.firebase import get_db, upload_image_to_storage

router = APIRouter(prefix="/cases")


@router.post("/", response_model=CaseResponse)
def create_case(
    case: CaseCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    case_id = str(uuid.uuid4())
    now_dt = datetime.now(timezone.utc)

    # Verify patient belongs to doctor if patient_id is provided
    if case.patient_id:
        patient_row = db.query(Patient).filter(Patient.id == case.patient_id).first()
        if patient_row and patient_row.doctor_id != current_user.uid and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to create case for this patient")

    # 1. Save to SQLite database
    new_case = Case(
        id=case_id,
        doctor_id=current_user.uid,
        patient_id=case.patient_id,
        status="Pending Analysis",
        notes=case.notes,
        created_at=now_dt
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # 2. Sync to Firestore (backup)
    try:
        fs_db = get_db()
        case_data = {
            "id": case_id,
            "doctor_id": current_user.uid,
            "patient_id": case.patient_id,
            "status": "Pending Analysis",
            "notes": case.notes,
            "created_at": now_dt.isoformat()
        }
        fs_db.collection("cases").document(case_id).set(case_data)
    except Exception as fs_err:
        print(f"Notice: Firestore case sync skipped: {fs_err}")

    return CaseResponse(
        id=new_case.id,
        doctor_id=new_case.doctor_id,
        patient_id=new_case.patient_id,
        status=new_case.status,
        notes=new_case.notes,
        created_at=new_case.created_at
    )


@router.get("/", response_model=List[CaseResponse])
def get_all_cases(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Retrieves all cases for the current authenticated user by merging SQL and Firestore.
    """
    case_map = {}

    # 1. Query SQL database
    try:
        db_cases = (
            db.query(Case)
            .filter(Case.doctor_id == current_user.uid)
            .order_by(Case.created_at.desc())
            .all()
        )
        for c in db_cases:
            if c.id:
                case_map[c.id] = CaseResponse(
                    id=c.id,
                    doctor_id=c.doctor_id,
                    patient_id=c.patient_id,
                    status=c.status,
                    notes=c.notes,
                    created_at=c.created_at
                )
    except Exception as sql_err:
        print(f"SQL cases fetch notice: {sql_err}")

    # 2. Query Firestore cases
    try:
        fs_db = get_db()
        for field in ["doctor_id", "doctorId", "user_id"]:
            try:
                docs = fs_db.collection("cases").where(field, "==", current_user.uid).stream()
                for doc in docs:
                    d = doc.to_dict()
                    c_id = d.get("id") or doc.id
                    if c_id and c_id not in case_map:
                        created_dt = None
                        if "created_at" in d and isinstance(d["created_at"], str):
                            try:
                                created_dt = datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                            except Exception:
                                pass
                        elif "createdAt" in d and isinstance(d["createdAt"], (int, float)):
                            created_dt = datetime.fromtimestamp(d["createdAt"] / 1000, tz=timezone.utc)

                        case_map[c_id] = CaseResponse(
                            id=c_id,
                            doctor_id=d.get("doctor_id") or current_user.uid,
                            patient_id=d.get("patient_id") or d.get("patientId"),
                            status=d.get("status") or "completed",
                            notes=d.get("notes"),
                            created_at=created_dt
                        )
            except Exception:
                pass
    except Exception as fs_err:
        print(f"Firestore cases fetch notice: {fs_err}")

    return list(case_map.values())


@router.get("/patient/{patient_id}", response_model=List[CaseResponse])
def get_patient_cases(
    patient_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    case_map = {}

    # Query SQL database
    try:
        db_cases = (
            db.query(Case)
            .filter(Case.patient_id == patient_id)
            .order_by(Case.created_at.desc())
            .all()
        )
        for c in db_cases:
            if c.id:
                case_map[c.id] = CaseResponse(
                    id=c.id,
                    doctor_id=c.doctor_id,
                    patient_id=c.patient_id,
                    status=c.status,
                    notes=c.notes,
                    created_at=c.created_at
                )
    except Exception:
        pass

    # Fallback to Firestore
    try:
        fs_db = get_db()
        docs = fs_db.collection("cases").where("patient_id", "==", patient_id).stream()
        for doc in docs:
            d = doc.to_dict()
            c_id = d.get("id") or doc.id
            if c_id and c_id not in case_map:
                created_dt = None
                if "created_at" in d and isinstance(d["created_at"], str):
                    try:
                        created_dt = datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                    except Exception:
                        pass
                case_map[c_id] = CaseResponse(
                    id=c_id,
                    doctor_id=d.get("doctor_id", current_user.uid),
                    patient_id=d.get("patient_id", patient_id),
                    status=d.get("status", "completed"),
                    notes=d.get("notes"),
                    created_at=created_dt
                )
    except Exception:
        pass

    return list(case_map.values())


@router.post("/{case_id}/upload")
async def upload_case_image(
    case_id: str,
    file: UploadFile = File(...),
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Upload an image (OPG/Photo) for a specific case.
    Stores the image in local storage and records in SQL database.
    """
    image_bytes = await file.read()
    image_id = str(uuid.uuid4())
    filename = file.filename or f"{image_id}.jpg"
    now_dt = datetime.now(timezone.utc)

    # Save to disk
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", f"{image_id}_{filename}")
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    base_url = os.getenv("PUBLIC_BASE_URL", os.getenv("BASE_URL", "https://orthofinixai-backend.onrender.com"))
    storage_url = f"{base_url}/uploads/{image_id}_{filename}"

    # Save in SQL database
    image_record = UploadedImage(
        id=image_id,
        user_id=current_user.uid,
        case_id=case_id,
        filename=filename,
        file_path=file_path,
        storage_url=storage_url,
        content_type=file.content_type or "image/jpeg",
        view_type="case_attachment",
        uploaded_at=now_dt
    )
    db.add(image_record)
    db.commit()

    # Firestore backup
    try:
        fs_db = get_db()
        image_data = {
            "id": image_id,
            "case_id": case_id,
            "filename": filename,
            "content_type": file.content_type or "image/jpeg",
            "storage_url": storage_url,
            "uploaded_at": now_dt.isoformat()
        }
        fs_db.collection("images").document(image_id).set(image_data)
    except Exception as fs_err:
        print(f"Notice: Firestore image sync skipped: {fs_err}")

    return {"message": "Image uploaded successfully", "image_id": image_id, "url": storage_url}


@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Deletes a case record and delegates to authoritative analysis deletion logic.
    """
    from app.api.routes.analysis import delete_analysis
    return await delete_analysis(case_id, current_user, db)
