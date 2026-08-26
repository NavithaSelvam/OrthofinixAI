from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import time

@dataclass
class ModelInferenceResult:
    """
    Standardized inference payload returned by all production ClinicalAIModel engines.
    """
    model_name: str
    model_version: str
    inference_time_ms: float
    confidence_score: float
    view_type: str
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    coordinates: Dict[str, Any] = field(default_factory=dict)
    masks: Dict[str, Any] = field(default_factory=dict)
    keypoints: Dict[str, Any] = field(default_factory=dict)
    validation_status: str = "success"
    error_message: Optional[str] = None

class ClinicalAIModel(ABC):
    """
    Abstract base class for all production OrthofinixAI deep learning inference engines.
    Enforces ONNX Runtime session management, tensor preprocessing, and validated output decoding.
    """
    def __init__(self, model_name: str, model_version: str, model_path: Optional[str] = None):
        self.model_name = model_name
        self.model_version = model_version
        self.model_path = model_path
        self.session = None
        if model_path:
            self.load_model(model_path)

    @abstractmethod
    def load_model(self, model_path: str):
        """
        Loads the ONNX inference session and verifies input/output signatures.
        """
        pass

    @abstractmethod
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesses raw image to tensor with normalized dimensions and dtype.
        """
        pass

    @abstractmethod
    def predict(self, image: np.ndarray, view_type: str = "frontal") -> ModelInferenceResult:
        """
        Executes model inference and decodes structured findings with confidence scores.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_path": self.model_path,
            "is_loaded": self.session is not None
        }

# Alias for backwards compatibility with legacy base class references
OrthodonticModel = ClinicalAIModel
