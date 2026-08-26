"""Maps AI engine output to standard AnalysisReport ORM entity and API response."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.orm_models import AnalysisReport
from app.services.ai_engine import ai_engine


def _extract_metrics(result: dict) -> Dict[str, Any]:
    details = result.get("details") or {}
    lateral = details.get("overjet_overbite") or {}
    andrews = details.get("andrews_details") or {}
    symmetry = details.get("arch_symmetry") or {}
    opg = details.get("opg_parallelism") or {}

    midline = symmetry.get("midline_deviation_mm", 0.0)
    overjet = lateral.get("overjet_mm")
    overbite = lateral.get("overbite_percent")

    finishing = result.get("finishing_score", 0.0)

    molar_left = "Unavailable"
    molar_right = "Unavailable"
    if isinstance(andrews, list):
        molar_details = next((k for k in andrews if "Molar" in k.get("key", "")), {})
        molar_left = molar_details.get("details", {}).get("left", {}).get("classification", "Unavailable")
        molar_right = molar_details.get("details", {}).get("right", {}).get("classification", "Unavailable")

    arch_sym = result.get("arch_symmetry_score")
    if arch_sym is None:
        arch_sym = result.get("alignment_score", 0.0)
        
    root_ang = result.get("root_angulation_score")
    if root_ang is None:
        root_ang = 0.0

    return {
        "midline_deviation_mm": round(float(midline), 1) if midline is not None else 0.0,
        "overjet_mm": round(float(overjet), 1) if overjet is not None else 0.0,
        "overbite_percent": round(float(overbite), 1) if overbite is not None else 0.0,
        "finishing_score": round(float(finishing), 1) if finishing is not None else 0.0,
        "alignment_score": round(float(arch_sym), 1),
        "root_angulation_score": round(float(root_ang), 1),
        "molar_right": molar_right,
        "molar_left": molar_left,
        "view_type": result.get("view_type", "frontal"),
        "model_metadata": result.get("model_metadata", {}),
        "measured_values": result.get("measured_values", {}),
        "calculated_scores": result.get("calculated_scores", {}),
        "unavailable_measurements": result.get("unavailable_measurements", []),
        "warnings": details.get("warnings", []),
        "conflicts": details.get("conflicts", []),
    }


def build_report_from_ai(
    db: Session,
    user_id: str,
    image_bytes: bytes,
    patient_name: str,
    image_url: str,
    view_type: str = "frontal",
) -> AnalysisReport:
    result = ai_engine.analyze_image(image_bytes, view_type=view_type)
    metrics = _extract_metrics(result)
    report_id = str(uuid.uuid4())

    report = AnalysisReport(
        id=report_id,
        user_id=user_id,
        patient_name=patient_name,
        image_url=image_url,
        view_type=view_type,
        status="completed" if result.get("status") != "failed_detection" else "failed_detection",
        finishing_score=metrics["finishing_score"],
        alignment_score=metrics["alignment_score"],
        confidence_score=float(result.get("confidence_score", 0.0)) * 100,
        midline_deviation_mm=metrics["midline_deviation_mm"],
        overjet_mm=metrics["overjet_mm"],
        overbite_percent=metrics["overbite_percent"],
        abo_score=float(result.get("abo_score", 0.0)),
        andrews_score=float(result.get("andrews_score", 0.0)),
        prediction=result.get("prediction", "Analysis complete."),
        recommendations_json=json.dumps(result.get("recommendations", [])),
        metrics_json=json.dumps({**metrics, "details": result.get("details", {})}),
        created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def report_to_response(report: AnalysisReport):
    from app.models.summit_schemas import AnalysisReportResponse
    import json as _json

    return AnalysisReportResponse(
        id=report.id,
        patient_name=report.patient_name,
        image_url=report.image_url,
        view_type=report.view_type,
        status=report.status,
        finishing_score=report.finishing_score,
        alignment_score=report.alignment_score,
        confidence_score=report.confidence_score,
        midline_deviation_mm=report.midline_deviation_mm,
        overjet_mm=report.overjet_mm,
        overbite_percent=report.overbite_percent,
        abo_score=report.abo_score,
        andrews_score=report.andrews_score,
        prediction=report.prediction,
        recommendations=_json.loads(report.recommendations_json or "[]"),
        metrics=_json.loads(report.metrics_json or "{}"),
        created_at=report.created_at,
    )
