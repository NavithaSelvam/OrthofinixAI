import math
import numpy as np
from typing import Tuple, List, Dict, Any, Union, Optional

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates the Euclidean distance between two 2D points."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def calculate_angle_between_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """Calculates the angle in degrees between two 2D vectors."""
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    denom = (math.sqrt(v1[0]**2 + v1[1]**2) * math.sqrt(v2[0]**2 + v2[1]**2))
    if denom == 0:
        return 0.0
    val = dot_product / denom
    val = max(-1.0, min(1.0, val))
    return math.degrees(math.acos(val))

def project_vector(v: Tuple[float, float], u: Tuple[float, float]) -> Tuple[float, float]:
    """Projects vector v onto vector u."""
    u_len_sq = u[0]**2 + u[1]**2
    if u_len_sq == 0:
        return (0.0, 0.0)
    dot_product = v[0] * u[0] + v[1] * u[1]
    factor = dot_product / u_len_sq
    return (factor * u[0], factor * u[1])

def project_vector_magnitude(v: Tuple[float, float], u: Tuple[float, float]) -> float:
    """Calculates the signed magnitude of vector v projected onto vector u."""
    u_len = math.sqrt(u[0]**2 + u[1]**2)
    if u_len == 0:
        return 0.0
    dot_product = v[0] * u[0] + v[1] * u[1]
    return dot_product / u_len

def fit_occlusal_plane(
    data: Union[Dict[str, Tuple[float, float]], List[Tuple[float, float]]],
    segmented_teeth: Optional[Dict[int, Dict[str, Any]]] = None
) -> Tuple[Tuple[float, float], Dict[str, float]]:
    """
    Fits a straight line representing the occlusal plane through incisal edges and molar cusps.
    Returns:
      - v_op_norm: Tuple[float, float] (normalized directional vector along plane)
      - line_dict: Dict[str, float] with 'slope' and 'intercept'
    """
    pts_list: List[Tuple[float, float]] = []
    
    if isinstance(data, dict):
        # Extract incisal edges, cusps, and midpoints
        for k, v in data.items():
            if any(term in k for term in ["incisal", "cusp", "midpoint"]):
                if isinstance(v, (tuple, list)) and len(v) >= 2:
                    pts_list.append((float(v[0]), float(v[1])))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                pts_list.append((float(item[0]), float(item[1])))

    if segmented_teeth:
        for t in segmented_teeth.values():
            if "centroid" in t:
                pts_list.append((float(t["centroid"][0]), float(t["centroid"][1])))

    if len(pts_list) < 2:
        return (1.0, 0.0), {"slope": 0.0, "intercept": 0.5}

    pts = np.array(pts_list)
    x = pts[:, 0]
    y = pts[:, 1]
    
    # Linear least squares
    A = np.vstack([x, np.ones(len(x))]).T
    try:
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    except Exception:
        m, c = 0.0, 0.5

    v_op = (1.0, float(m))
    v_op_len = math.sqrt(1.0 + m**2)
    v_op_norm = (1.0 / v_op_len, float(m) / v_op_len)

    return v_op_norm, {"slope": round(float(m), 4), "intercept": round(float(c), 4)}
