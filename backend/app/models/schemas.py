from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, timezone

class UserInfo(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    role: str = "doctor"

class PatientBase(BaseModel):
    name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    contact_info: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: str
    doctor_id: str
    created_at: Optional[datetime] = None

class CaseBase(BaseModel):
    patient_id: Optional[str] = None
    notes: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: str
    doctor_id: Optional[str] = None
    status: str = "Pending Analysis"
    created_at: Optional[datetime] = None

class UploadResponse(BaseModel):
    upload_id: str
    image_url: str
    filename: Optional[str] = None

class PredictionResponse(BaseModel):
    prediction: str
    confidence_score: float
    recommendations: List[str]
    details: Optional[Dict[str, Any]] = None

class ToothFindingItem(BaseModel):
    toothNumber: int
    name: str
    score: float = 0.0
    status: str = "Aligned"
    issues: List[str] = Field(default_factory=list)

from pydantic import BaseModel, Field, field_validator

class AnalysisHistoryItem(BaseModel):
    id: str
    patient_name: str
    overallScore: Optional[float] = None
    overall_finishing_score: Optional[float] = None
    finishing_score: float = 0
    confidence: Optional[float] = None
    confidence_score: float = 0
    alignmentScore: Optional[float] = None
    alignment_score: Optional[float] = None
    teeth: Optional[List[Dict[str, Any]]] = None
    teeth_data: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[Any] = None
    image_url: Optional[str] = None
    user_id: Optional[str] = None

    @field_validator("created_at", mode="before")
    def parse_created_at(cls, v):
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, tz=timezone.utc).isoformat()
        return str(v)

class AnalysisReportResponse(BaseModel):
    id: str
    case_id: Optional[str] = None
    user_id: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: str
    image_url: Optional[str] = None
    view_type: str = "frontal"
    status: str = "completed"
    overallScore: Optional[float] = None
    overall_finishing_score: Optional[float] = None
    finishing_score: float = 0
    confidence: Optional[float] = None
    confidence_score: float = 0
    alignmentScore: Optional[float] = None
    alignment_score: float = 0
    arch_symmetry_score: Optional[float] = 0
    teeth: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    teeth_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    midline_deviation_mm: float = 0
    overjet_mm: float = 0
    overbite_percent: float = 0
    abo_score: float = 0
    andrews_score: float = 0
    root_angulation_score: float = 0
    prediction: str = ""
    recommendations: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    images: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    image_count: Optional[int] = 1
    views: Optional[List[str]] = Field(default_factory=list)
    landmarks: Optional[Dict[str, Any]] = Field(default_factory=dict)
    teeth_detections: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    root_measurements: Optional[Dict[str, Any]] = Field(default_factory=dict)
    occlusal_plane: Optional[Dict[str, Any]] = Field(default_factory=dict)
    arch_measurements: Optional[Dict[str, Any]] = Field(default_factory=dict)
    clinical_metrics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    analysis_type: Optional[str] = "computer_vision_heuristic"
    engine_name: Optional[str] = "OrthofinixAI Clinical Vision & Morphometric Engine"
    engine_version: Optional[str] = "2.0.0"
    limitations: Optional[str] = "Automated computer-vision heuristic landmarking and geometric measurements for clinical decision support. Not a standalone diagnostic device."
    created_at: Optional[str] = None


class RecalculateRequest(BaseModel):
    landmarks: Dict[str, Tuple[float, float]]
    segmented_teeth: Optional[Dict[int, Dict[str, Any]]] = None
    view_type: str = "frontal"
    bracket_pixel_width: Optional[float] = 30.0
    scale_factor: Optional[float] = None

class AIReportResponse(BaseModel):
    id: str
    case_id: str
    image_url: Optional[str] = None
    abo_score: float
    arch_symmetry_score: float
    root_angulation_score: float
    andrews_score: float
    recommendations: List[str]
    details: Optional[Any] = None
    created_at: datetime

# Posts / Clinical Discussions / Notes
class PostBase(BaseModel):
    title: str
    content: str
    category: str = "clinical_discussion"
    image_url: Optional[str] = None
    report_id: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class PostResponse(PostBase):
    id: str
    user_id: str
    author_name: Optional[str] = "Doctor"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
