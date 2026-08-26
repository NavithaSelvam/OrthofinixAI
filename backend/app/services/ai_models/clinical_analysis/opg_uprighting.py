import math
from typing import Dict, Tuple, List, Any, Optional

class OPGUprightingAnalyzer:
    """
    Analyzes panoramic radiographs (OPGs) to evaluate root parallelism,
    root divergence/convergence, and generate clinical uprighting recommendations.
    """
    
    @staticmethod
    def calculate_root_angulation(
        apex: Tuple[float, float], 
        crown: Tuple[float, float], 
        v_op_norm: Tuple[float, float],
        is_upper: bool
    ) -> float:
        """
        Calculates root angulation in degrees relative to the normal of the occlusal plane.
        """
        xa, ya = apex
        xc, yc = crown
        
        dy = ya - yc
        dx = xa - xc
        
        angle_rad = math.atan2(dy, dx) if dx != 0 else (math.pi / 2 if dy > 0 else -math.pi / 2)
        angle_deg = math.degrees(angle_rad)
        
        deviation = (angle_deg + 90.0) if is_upper else (angle_deg - 90.0)
        while deviation > 180.0:
            deviation -= 360.0
        while deviation < -180.0:
            deviation += 360.0
            
        return round(deviation, 2)

    @staticmethod
    def analyze_parallelism(
        landmarks: Dict[str, Tuple[float, float]],
        v_op_norm: Tuple[float, float],
        scale_factor: float,
        view_type: str = "opg",
        opg_data: Optional[Dict[int, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates root angulation for all detected teeth and compares adjacent roots.
        """
        if view_type != "opg":
            return {
                "parallelism_score": None,
                "status": "Unavailable for Non-OPG View",
                "angulations": {},
                "deviations": [],
                "explanation": "Root parallelism and angulation analysis requires a panoramic radiograph (OPG) or full-mouth periapical series. Intraoral photography cannot visualize bone-embedded roots."
            }

        angulations = {}
        upper_teeth = []
        lower_teeth = []
        
        # Use direct OPG model predictions if supplied
        if opg_data:
            for fdi, data in opg_data.items():
                apex = data["apex"]
                crown = data["crown"]
                is_upper = (fdi < 30)
                ang = OPGUprightingAnalyzer.calculate_root_angulation(apex, crown, v_op_norm, is_upper)
                angulations[fdi] = {"angulation": ang, "is_upper": is_upper, "apex": apex, "crown": crown}
                if is_upper:
                    upper_teeth.append(fdi)
                else:
                    lower_teeth.append(fdi)
        else:
            # Parse from landmarks dict
            for key, apex in landmarks.items():
                if key.endswith("_apex"):
                    fdi_str = key.split("_")[0]
                    try:
                        fdi = int(fdi_str)
                    except ValueError:
                        continue
                    mid_key = f"{fdi}_midpoint"
                    if mid_key in landmarks:
                        crown = landmarks[mid_key]
                        is_upper = (fdi < 30)
                        ang = OPGUprightingAnalyzer.calculate_root_angulation(apex, crown, v_op_norm, is_upper)
                        angulations[fdi] = {"angulation": ang, "is_upper": is_upper, "apex": apex, "crown": crown}
                        if is_upper:
                            upper_teeth.append(fdi)
                        else:
                            lower_teeth.append(fdi)
                            
        if not angulations:
            return {
                "parallelism_score": None,
                "status": "Measurement Unavailable",
                "angulations": {},
                "deviations": [],
                "explanation": "Root apices and crown trajectories not detectable in this panoramic image."
            }

        sorted_upper = sorted([t for t in upper_teeth if t < 20], reverse=True) + sorted([t for t in upper_teeth if t >= 20])
        sorted_lower = sorted([t for t in lower_teeth if t >= 40], reverse=True) + sorted([t for t in lower_teeth if t < 40])
        
        deviations = []
        parallelism_score_sum = 0.0
        comparisons_count = 0
        
        for t_list, jaw_name in [(sorted_upper, "upper"), (sorted_lower, "lower")]:
            for i in range(len(t_list) - 1):
                t1, t2 = t_list[i], t_list[i+1]
                ang1 = angulations[t1]["angulation"]
                ang2 = angulations[t2]["angulation"]
                dev = abs(ang1 - ang2)
                
                status = "Parallel" if dev <= 5.0 else "Divergent" if (ang1 * ang2 < 0) else "Convergent"
                severity = "Normal" if dev <= 5.0 else "Mild" if dev <= 8.0 else "Moderate" if dev <= 12.0 else "Severe"
                
                deviations.append({
                    "teeth": (t1, t2),
                    "angulation_1": ang1,
                    "angulation_2": ang2,
                    "deviation_angle": round(dev, 2),
                    "status": status,
                    "severity": severity,
                    "jaw": jaw_name
                })
                parallelism_score_sum += max(0.0, 1.0 - (dev / 15.0))
                comparisons_count += 1
                
        final_score = (parallelism_score_sum / comparisons_count * 100.0) if comparisons_count > 0 else 100.0
        final_status = "Optimal Root Parallelism" if final_score >= 85.0 else "Root Convergence/Divergence Detected"
        
        return {
            "parallelism_score": round(final_score, 1),
            "status": final_status,
            "angulations": {fdi: data["angulation"] for fdi, data in angulations.items()},
            "deviations": deviations,
            "explanation": f"Root parallelism score is {round(final_score, 1)}%. Found {len([d for d in deviations if d['severity'] != 'Normal'])} non-parallel root pairs."
        }
