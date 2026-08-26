from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from app.models.schemas import PatientCreate, PatientResponse, UserInfo
from app.api.dependencies import get_current_user
from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import Patient, Case, AnalysisReport, UploadedImage
from app.db.firebase import get_db, delete_firestore_patient

router = APIRouter(prefix="/patients")


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    patient_id = str(uuid.uuid4())
    now_dt = datetime.now(timezone.utc)

    # 1. Save to SQLite database
    new_patient = Patient(
        id=patient_id,
        doctor_id=current_user.uid,
        name=patient.name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        contact_info=patient.contact_info,
        created_at=now_dt
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # 2. Sync to Firestore (backup)
    try:
        fs_db = get_db()
        patient_data = {
            "id": patient_id,
            "doctor_id": current_user.uid,
            "name": patient.name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "contact_info": patient.contact_info,
            "created_at": now_dt.isoformat()
        }
        fs_db.collection("patients").document(patient_id).set(patient_data)
    except Exception as fs_err:
        print(f"Notice: Firestore patient sync skipped: {fs_err}")

    return PatientResponse(
        id=new_patient.id,
        doctor_id=new_patient.doctor_id,
        name=new_patient.name,
        date_of_birth=new_patient.date_of_birth,
        gender=new_patient.gender,
        contact_info=new_patient.contact_info,
        created_at=new_patient.created_at
    )


@router.get("/", response_model=List[PatientResponse])
def get_patients(
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Retrieves all patients for current doctor by merging SQL database and Firestore.
    """
    patient_map = {}

    # 1. Query SQL database
    try:
        db_patients = (
            db.query(Patient)
            .filter(Patient.doctor_id == current_user.uid)
            .order_by(Patient.created_at.desc())
            .all()
        )
        for p in db_patients:
            if p.id:
                patient_map[p.id] = PatientResponse(
                    id=p.id,
                    doctor_id=p.doctor_id,
                    name=p.name,
                    date_of_birth=p.date_of_birth,
                    gender=p.gender,
                    contact_info=p.contact_info,
                    created_at=p.created_at
                )
    except Exception as sql_err:
        print(f"SQL patients fetch notice: {sql_err}")

    # 2. Query Firestore patients collection across field variants
    try:
        fs_db = get_db()
        for field in ["doctor_id", "doctorId"]:
            try:
                docs = fs_db.collection("patients").where(field, "==", current_user.uid).stream()
                for doc in docs:
                    d = doc.to_dict()
                    p_id = d.get("id") or doc.id
                    if p_id and p_id not in patient_map:
                        created_dt = None
                        if "created_at" in d and isinstance(d["created_at"], str):
                            try:
                                created_dt = datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                            except Exception:
                                pass
                        elif "createdAt" in d and isinstance(d["createdAt"], (int, float)):
                            created_dt = datetime.fromtimestamp(d["createdAt"] / 1000, tz=timezone.utc)

                        patient_map[p_id] = PatientResponse(
                            id=p_id,
                            doctor_id=d.get("doctor_id") or d.get("doctorId") or current_user.uid,
                            name=d.get("name") or d.get("patient_name") or d.get("patientName") or "Patient",
                            date_of_birth=d.get("date_of_birth") or d.get("dateOfBirth") or d.get("dob"),
                            gender=d.get("gender") or "Unknown",
                            contact_info=d.get("contact_info") or d.get("phone") or "",
                            created_at=created_dt
                        )
            except Exception:
                pass

        if current_user.email:
            try:
                docs = fs_db.collection("patients").where("doctor_email", "==", current_user.email).stream()
                for doc in docs:
                    d = doc.to_dict()
                    p_id = d.get("id") or doc.id
                    if p_id and p_id not in patient_map:
                        patient_map[p_id] = PatientResponse(
                            id=p_id,
                            doctor_id=d.get("doctor_id") or current_user.uid,
                            name=d.get("name") or d.get("patient_name") or "Patient",
                            date_of_birth=d.get("date_of_birth") or d.get("dob"),
                            gender=d.get("gender") or "Unknown",
                            contact_info=d.get("contact_info") or d.get("phone") or "",
                            created_at=None
                        )
            except Exception:
                pass
    except Exception as fs_err:
        print(f"Firestore patients fetch notice: {fs_err}")

    return list(patient_map.values())


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    # Check SQL database
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if p:
        if p.doctor_id != current_user.uid and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view this patient")
        return PatientResponse(
            id=p.id,
            doctor_id=p.doctor_id,
            name=p.name,
            date_of_birth=p.date_of_birth,
            gender=p.gender,
            contact_info=p.contact_info,
            created_at=p.created_at
        )

    # Fallback to Firestore
    try:
        fs_db = get_db()
        doc = fs_db.collection("patients").document(patient_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("doctor_id") != current_user.uid and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to view this patient")
            return PatientResponse(
                id=data.get("id", patient_id),
                doctor_id=data.get("doctor_id", current_user.uid),
                name=data.get("name", "Unknown"),
                date_of_birth=data.get("date_of_birth"),
                gender=data.get("gender"),
                contact_info=data.get("contact_info"),
                created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data and isinstance(data["created_at"], str) else None
            )
    except HTTPException:
        raise
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Patient not found")


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: str,
    current_user: UserInfo = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Deletes a patient and all associated cases and analysis reports from SQL database and Firestore.
    """
    # 1. SQL cascade delete
    try:
        cases = db.query(Case).filter(Case.patient_id == patient_id).all()
        for c in cases:
            db.query(AnalysisReport).filter(AnalysisReport.id == c.id).delete()
            db.query(UploadedImage).filter(UploadedImage.case_id == c.id).delete()
        db.query(Case).filter(Case.patient_id == patient_id).delete()
        db.query(Patient).filter(Patient.id == patient_id).delete()
        db.commit()
    except Exception as sql_err:
        db.rollback()
        print(f"Notice during SQL patient deletion: {sql_err}")

    # 2. Firestore cascade delete
    try:
        delete_firestore_patient(patient_id, current_user.uid)
    except Exception as fs_err:
        print(f"Notice during Firestore patient deletion: {fs_err}")

    return {
        "status": "success",
        "message": "Patient and all associated cases deleted successfully",
        "deleted_id": patient_id
    }

