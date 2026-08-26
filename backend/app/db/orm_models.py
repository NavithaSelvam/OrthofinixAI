from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.sqlalchemy_db import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users_orm"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True, default="")
    display_name = Column(String, default="Doctor")
    role = Column(String, default="doctor")
    created_at = Column(DateTime, default=utcnow)

    patients = relationship("Patient", back_populates="doctor", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="doctor", cascade="all, delete-orphan")
    analyses = relationship("AnalysisReport", back_populates="user", cascade="all, delete-orphan")
    images = relationship("UploadedImage", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


class Patient(Base):
    __tablename__ = "patients_orm"

    id = Column(String, primary_key=True)
    doctor_id = Column(String, ForeignKey("users_orm.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    contact_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    doctor = relationship("User", back_populates="patients")
    cases = relationship("Case", back_populates="patient", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases_orm"

    id = Column(String, primary_key=True)
    doctor_id = Column(String, ForeignKey("users_orm.id"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients_orm.id"), nullable=True, index=True)
    status = Column(String, default="Pending Analysis")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    doctor = relationship("User", back_populates="cases")
    patient = relationship("Patient", back_populates="cases")
    images = relationship("UploadedImage", back_populates="case")
    analyses = relationship("AnalysisReport", back_populates="case")


class UploadedImage(Base):
    __tablename__ = "uploaded_images_orm"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users_orm.id"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases_orm.id"), nullable=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    storage_url = Column(String, nullable=False)
    content_type = Column(String, default="image/jpeg")
    view_type = Column(String, default="frontal")
    uploaded_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="images")
    case = relationship("Case", back_populates="images")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users_orm.id"), nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients_orm.id"), nullable=True, index=True)
    case_id = Column(String, ForeignKey("cases_orm.id"), nullable=True, index=True)
    patient_name = Column(String, default="Patient")
    image_url = Column(String, nullable=True)
    view_type = Column(String, default="frontal")
    status = Column(String, default="completed")

    finishing_score = Column(Float, default=0.0)
    alignment_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    midline_deviation_mm = Column(Float, default=0.0)
    overjet_mm = Column(Float, default=0.0)
    overbite_percent = Column(Float, default=0.0)
    abo_score = Column(Float, default=0.0)
    andrews_score = Column(Float, default=0.0)
    root_angulation_score = Column(Float, default=0.0)

    prediction = Column(Text, default="")
    recommendations_json = Column(Text, default="[]")
    metrics_json = Column(Text, default="{}")

    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="analyses")
    case = relationship("Case", back_populates="analyses")


class Post(Base):
    __tablename__ = "posts_orm"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users_orm.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default="clinical_discussion")
    image_url = Column(String, nullable=True)
    report_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    author = relationship("User", back_populates="posts")
