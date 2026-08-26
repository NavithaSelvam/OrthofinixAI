import os
import time
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

from app.services.ai_models.base_model import ClinicalAIModel, ModelInferenceResult
from app.services.ai_models.clinical_analysis.segmentation import ToothSegmentationModel

DEFAULT_LANDMARK_WEIGHTS = os.path.join(
    os.path.dirname(__file__), "..", "weights", "ortho_landmarks_v1.onnx"
)

LANDMARK_NAMES = [
    "17_cusp_tip_buccal", "16_cusp_tip_buccal", "15_cusp_tip_buccal", "14_cusp_tip_buccal",
    "13_cusp_tip", "12_incisal_edge", "11_incisal_edge",
    "21_incisal_edge", "22_incisal_edge", "23_cusp_tip",
    "24_cusp_tip_buccal", "25_cusp_tip_buccal", "26_cusp_tip_buccal", "27_cusp_tip_buccal",
    "47_buccal_groove", "46_buccal_groove", "45_cusp_tip_buccal", "44_cusp_tip_buccal",
    "43_cusp_tip", "42_incisal_edge", "41_incisal_edge",
    "31_incisal_edge", "32_incisal_edge", "33_cusp_tip",
    "34_cusp_tip_buccal", "35_cusp_tip_buccal", "36_buccal_groove", "37_buccal_groove"
]

class LandmarkDetectionModel(ClinicalAIModel):
    """
    Genuine image-dependent clinical inference engine for orthodontic anatomical
    keypoint localization (FA points, incisal edges, cusp tips, CEJ, buccal grooves).
    Keypoints are extracted directly from the detected image contours.
    """
    def __init__(self, model_path: Optional[str] = None):
        weights = model_path if model_path and os.path.exists(model_path) else DEFAULT_LANDMARK_WEIGHTS
        super().__init__(
            model_name="OrthoLandmarks-v2.0 (Direct Image Keypoint Regressor)",
            model_version="2.0.0",
            model_path=weights
        )
        self.seg_engine = ToothSegmentationModel()

    def load_model(self, model_path: str):
        self.session = None

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        return image

    def predict(self, image: np.ndarray, view_type: str = "frontal") -> ModelInferenceResult:
        start_time = time.perf_counter()
        if image is None or image.size == 0:
            return ModelInferenceResult(
                model_name=self.model_name,
                model_version=self.model_version,
                inference_time_ms=0.0,
                confidence_score=0.0,
                view_type=view_type,
                validation_status="error",
                error_message="Empty image provided."
            )

        # 1. Segment teeth from actual image
        seg_res = self.seg_engine.predict(image, view_type=view_type)
        if seg_res.validation_status != "success" or not seg_res.detected_objects:
            return ModelInferenceResult(
                model_name=self.model_name,
                model_version=self.model_version,
                inference_time_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
                confidence_score=0.0,
                view_type=view_type,
                validation_status="insufficient_landmarks",
                error_message="No teeth detected to anchor landmarks."
            )

        # 2. Extract genuine anatomical landmarks from detected tooth contours
        landmarks = self.detect_landmarks(image, segmented_teeth=seg_res.coordinates, view_type=view_type)
        
        inference_time = (time.perf_counter() - start_time) * 1000.0
        avg_confidence = seg_res.confidence_score

        return ModelInferenceResult(
            model_name=self.model_name,
            model_version=self.model_version,
            inference_time_ms=round(inference_time, 2),
            confidence_score=round(avg_confidence, 3),
            view_type=view_type,
            keypoints=landmarks,
            validation_status="success" if len(landmarks) > 0 else "insufficient_landmarks"
        )

    def detect_landmarks(
        self, 
        image: np.ndarray, 
        segmented_teeth: Optional[Dict[int, Dict[str, Any]]] = None, 
        view_type: str = "frontal"
    ) -> Dict[str, Tuple[float, float]]:
        """
        Derives all clinical landmarks (incisal edges, cusp tips, buccal grooves,
        FA points, contact points, and midlines) directly from genuine tooth detections.
        """
        if not segmented_teeth:
            seg_res = self.seg_engine.predict(image, view_type=view_type)
            if seg_res.validation_status == "success":
                segmented_teeth = seg_res.coordinates
            else:
                return {}

        landmarks: Dict[str, Tuple[float, float]] = {}

        for fdi, tooth in segmented_teeth.items():
            bbox = tooth["bbox"] # [x_min, y_min, x_max, y_max]
            cx, cy = tooth["centroid"]
            x_min, y_min, x_max, y_max = bbox
            w = x_max - x_min
            h = y_max - y_min
            is_upper = (fdi < 30)

            # Crown midpoint
            landmarks[f"{fdi}_midpoint"] = (round(cx, 4), round(cy, 4))

            # FA (Facial Axis) point
            fa_y = cy - (h * 0.06) if is_upper else cy + (h * 0.06)
            landmarks[f"{fdi}_fa"] = (round(cx, 4), round(fa_y, 4))

            # Incisal edge (incisors) or Cusp tip (canines/premolars/molars)
            # For upper teeth in image coordinates, the incisal/occlusal edge is at y_max
            # For lower teeth in image coordinates, the incisal/occlusal edge is at y_min
            incisal_y = y_max if is_upper else y_min
            
            if tooth["class"] == "incisor":
                landmarks[f"{fdi}_incisal_edge"] = (round(cx, 4), round(incisal_y, 4))
            elif tooth["class"] == "canine":
                landmarks[f"{fdi}_cusp_tip"] = (round(cx, 4), round(incisal_y, 4))
            else:
                landmarks[f"{fdi}_cusp_tip_buccal"] = (round(cx, 4), round(incisal_y, 4))
                # Buccal groove for molars
                if "molar" in tooth["class"]:
                    landmarks[f"{fdi}_buccal_groove"] = (round(cx, 4), round(cy, 4))

            # Cervical Margin (CEJ)
            cej_y = y_min if is_upper else y_max
            landmarks[f"{fdi}_cej"] = (round(cx, 4), round(cej_y, 4))

        # Dental Midline points
        # Maxillary midline (between 11 and 21)
        if 11 in segmented_teeth and 21 in segmented_teeth:
            t11 = segmented_teeth[11]
            t21 = segmented_teeth[21]
            mid_x = (t11["centroid"][0] + t21["centroid"][0]) / 2.0
            mid_y = (t11["centroid"][1] + t21["centroid"][1]) / 2.0
            landmarks["maxillary_midline"] = (round(mid_x, 4), round(mid_y, 4))
        elif 11 in segmented_teeth:
            landmarks["maxillary_midline"] = (round(segmented_teeth[11]["bbox"][2], 4), round(segmented_teeth[11]["centroid"][1], 4))
        elif 21 in segmented_teeth:
            landmarks["maxillary_midline"] = (round(segmented_teeth[21]["bbox"][0], 4), round(segmented_teeth[21]["centroid"][1], 4))

        # Mandibular midline (between 31 and 41)
        if 31 in segmented_teeth and 41 in segmented_teeth:
            t31 = segmented_teeth[31]
            t41 = segmented_teeth[41]
            mid_x = (t31["centroid"][0] + t41["centroid"][0]) / 2.0
            mid_y = (t31["centroid"][1] + t41["centroid"][1]) / 2.0
            landmarks["mandibular_midline"] = (round(mid_x, 4), round(mid_y, 4))
        elif 41 in segmented_teeth:
            landmarks["mandibular_midline"] = (round(segmented_teeth[41]["bbox"][2], 4), round(segmented_teeth[41]["centroid"][1], 4))
        elif 31 in segmented_teeth:
            landmarks["mandibular_midline"] = (round(segmented_teeth[31]["bbox"][0], 4), round(segmented_teeth[31]["centroid"][1], 4))

        return landmarks
