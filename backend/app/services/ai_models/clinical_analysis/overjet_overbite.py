import math
from typing import Dict, Tuple, Any, Optional
from .geometry import project_vector_magnitude, calculate_distance

class OverjetOverbiteAnalyzer:
    """
    Computes Overjet (OJ) and Overbite (OB) measurements with strict view gating.
    Overjet is evaluated only on Lateral views; Overbite is evaluated on Lateral and Frontal views.
    """
    
    @staticmethod
    def analyze_incisors(
        landmarks: Dict[str, Tuple[float, float]],
        v_op_norm: Tuple[float, float],
        scale_factor: float,
        view_type: str = "frontal"
    ) -> Dict[str, Any]:
        """
        Calculates overjet and overbite with view-specific clinical gating.
        """
        ui = landmarks.get("11_incisal_edge") or landmarks.get("21_incisal_edge")
        li = landmarks.get("41_incisal_edge") or landmarks.get("31_incisal_edge")
        
        # 1. Frontal View Handling
        if view_type == "frontal":
            if not ui or not li:
                return {
                    "overjet_mm": None,
                    "overbite_percent": None,
                    "overjet_status": "Unavailable for Frontal View",
                    "overjet_explanation": "Horizontal overjet clearance represents sagittal tooth separation. It requires a lateral profile view or cephalogram.",
                    "overbite_status": "Measurement Unavailable",
                    "overbite_explanation": "Incisor edge landmarks not detected."
                }
                
            # On frontal, vertical incisor overlap can be measured
            vertical_overlap_norm = li[1] - ui[1] # positive when upper incisor covers lower incisor
            vertical_overlap_mm = vertical_overlap_norm * scale_factor
            
            # Estimated crown height from standard proportion (~10mm)
            ob_percent = min(100.0, max(0.0, (vertical_overlap_mm / 10.0) * 100.0))
            
            ob_status = "Normal Overbite" if (20.0 <= ob_percent <= 40.0) else \
                        "Deep Bite" if ob_percent > 40.0 else "Reduced Overbite / Open Bite"
                        
            return {
                "overjet_mm": None,
                "overbite_percent": round(ob_percent, 1),
                "overjet_status": "Unavailable for Frontal View",
                "overjet_explanation": "Horizontal overjet clearance represents sagittal tooth separation. It requires a lateral profile view or cephalometric radiograph.",
                "overbite_status": ob_status,
                "overbite_explanation": f"Vertical incisor overlap is {round(ob_percent, 1)}% ({round(vertical_overlap_mm, 1)} mm)."
            }

        # 2. Lateral / Sagittal View Handling
        if not ui or not li:
            return {
                "overjet_mm": None,
                "overbite_percent": None,
                "overjet_status": "Measurement Unavailable",
                "overjet_explanation": "Upper or lower incisal edge landmark missing on lateral scan.",
                "overbite_status": "Measurement Unavailable",
                "overbite_explanation": "Upper or lower incisal edge landmark missing on lateral scan."
            }

        ux, uy = v_op_norm
        n_op = (-uy, ux)
        n_op_len = math.sqrt(n_op[0]**2 + n_op[1]**2)
        n_op_norm = (n_op[0]/n_op_len, n_op[1]/n_op_len) if n_op_len > 0 else (0.0, 1.0)
        
        # Horizontal vector along occlusal plane
        v_oj = (ui[0] - li[0], ui[1] - li[1])
        oj_normalized = project_vector_magnitude(v_oj, v_op_norm)
        oj_mm = oj_normalized * scale_factor
        
        # Vertical vector along occlusal perpendicular
        v_ob = (ui[0] - li[0], ui[1] - li[1])
        ob_normalized = project_vector_magnitude(v_ob, n_op_norm)
        ob_mm = abs(ob_normalized * scale_factor)
        
        ob_percent = min(100.0, max(0.0, (ob_mm / 10.0) * 100.0))
        
        oj_status = "Normal Overjet" if (2.0 <= oj_mm <= 4.0) else \
                    "Excessive Overjet (Class II)" if oj_mm > 4.0 else \
                    "Anterior Crossbite / Underjet" if oj_mm < 0.0 else "Edge-to-Edge"
                    
        ob_status = "Normal Overbite" if (20.0 <= ob_percent <= 40.0) else \
                    "Deep Bite" if ob_percent > 40.0 else "Reduced Overbite"
                    
        return {
            "overjet_mm": round(oj_mm, 2),
            "overbite_percent": round(ob_percent, 1),
            "overjet_status": oj_status,
            "overjet_explanation": f"Overjet measured at {round(oj_mm, 1)} mm.",
            "overbite_status": ob_status,
            "overbite_explanation": f"Overbite measured at {round(ob_percent, 1)}% ({round(ob_mm, 1)} mm)."
        }

# Legacy alias
analyze_lateral_incisors = OverjetOverbiteAnalyzer.analyze_incisors
