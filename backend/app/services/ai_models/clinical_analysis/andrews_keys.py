from typing import Dict, List, Tuple, Any, Optional
import math
import numpy as np
from .geometry import calculate_distance, calculate_angle_between_vectors, project_vector_magnitude

class AndrewsSixKeysAnalyzer:
    """
    Evaluates Andrews' Six Keys to Normal Occlusion using validated geometric mathematics,
    strict view routing, and verified anatomical landmarks.
    """

    # Ideal Crown Angulation (Key 2 - Tip) in degrees (Andrews standard)
    IDEAL_TIP = {
        11: 5.0, 12: 9.0, 13: 11.0, 14: 2.0, 15: 2.0, 16: 5.0, 17: 5.0, 18: 5.0,
        21: 5.0, 22: 9.0, 23: 11.0, 24: 2.0, 25: 2.0, 26: 5.0, 27: 5.0, 28: 5.0,
        31: 2.0, 32: 2.0, 33: 5.0, 34: 2.0, 35: 2.0, 36: 2.0, 37: 2.0, 38: 2.0,
        41: 2.0, 42: 2.0, 43: 5.0, 44: 2.0, 45: 2.0, 46: 2.0, 47: 2.0, 48: 2.0
    }

    @staticmethod
    def classify_molar_relationship_side(
        upper_mb_cusp: Tuple[float, float],
        lower_buccal_groove: Tuple[float, float],
        v_op_norm: Tuple[float, float],
        scale_factor: float,
        is_left_side: bool
    ) -> Dict[str, Any]:
        """
        Classifies molar relationships (Class I, II, or III) from a lateral/OPG perspective.
        Delta X = X_cusp - X_groove projected onto occlusal plane.
        """
        dx = upper_mb_cusp[0] - lower_buccal_groove[0]
        dy = upper_mb_cusp[1] - lower_buccal_groove[1]
        
        disparity_norm = dx * v_op_norm[0] + dy * v_op_norm[1]
        disparity_mm = disparity_norm * scale_factor
        
        if not is_left_side:
            disparity_mm = -disparity_mm
            
        if -1.5 <= disparity_mm <= 1.5:
            classification = "Class I"
            explanation = f"Normal molar occlusion. The mesiobuccal cusp of the upper first molar fits within the buccal groove of the lower first molar (deviation: {round(disparity_mm, 1)} mm)."
            severity = "Normal"
            score = 1.0
        elif disparity_mm > 1.5:
            classification = "Class II"
            severity = "Mild" if disparity_mm <= 3.5 else "Moderate" if disparity_mm <= 5.5 else "Severe"
            explanation = f"Class II relationship detected. Upper molar cusp is mesial to lower groove by {round(disparity_mm, 1)} mm."
            score = max(0.0, 1.0 - (disparity_mm - 1.5) / 5.0)
        else:
            classification = "Class III"
            severity = "Mild" if disparity_mm >= -3.5 else "Moderate" if disparity_mm >= -5.5 else "Severe"
            explanation = f"Class III relationship detected. Upper molar cusp is distal to lower groove by {round(abs(disparity_mm), 1)} mm."
            score = max(0.0, 1.0 - (abs(disparity_mm) - 1.5) / 5.0)
            
        return {
            "classification": classification,
            "disparity_mm": round(disparity_mm, 2),
            "severity": severity,
            "explanation": explanation,
            "score": round(score, 2)
        }

    @staticmethod
    def analyze_key1_molar(
        landmarks: Dict[str, Tuple[float, float]], 
        v_op_norm: Tuple[float, float], 
        scale_factor: float
    ) -> Dict[str, Any]:
        """Key 1: Molar Relationship (analyzes left and right independently)"""
        u16 = landmarks.get("16_cusp_tip_buccal")
        l46 = landmarks.get("46_buccal_groove")
        u26 = landmarks.get("26_cusp_tip_buccal")
        l36 = landmarks.get("36_buccal_groove")
        
        results = {}
        scores = []
        
        if u16 and l46:
            r_res = AndrewsSixKeysAnalyzer.classify_molar_relationship_side(u16, l46, v_op_norm, scale_factor, is_left_side=False)
            results["right"] = r_res
            scores.append(r_res["score"])
        else:
            results["right"] = {
                "classification": "Unavailable",
                "disparity_mm": None,
                "severity": "N/A",
                "explanation": "Molar landmarks (16 cusp / 46 groove) not visible or obstructed in this view.",
                "score": None
            }
            
        if u26 and l36:
            l_res = AndrewsSixKeysAnalyzer.classify_molar_relationship_side(u26, l36, v_op_norm, scale_factor, is_left_side=True)
            results["left"] = l_res
            scores.append(l_res["score"])
        else:
            results["left"] = {
                "classification": "Unavailable",
                "disparity_mm": None,
                "severity": "N/A",
                "explanation": "Molar landmarks (26 cusp / 36 groove) not visible or obstructed in this view.",
                "score": None
            }
            
        if scores:
            avg_score = sum(scores) / len(scores)
            status = "Class I Occlusion" if avg_score > 0.9 else "Class II/III Malocclusion Tendency"
            explanation = f"Right side: {results['right']['classification']}. Left side: {results['left']['classification']}."
        else:
            avg_score = None
            status = "Measurement Unavailable"
            explanation = "Posterior molar landmarks are not visible in this image view."
            
        return {
            "key": "Key 1: Molar Relationship",
            "status": status,
            "score": round(avg_score, 2) if avg_score is not None else None,
            "details": results,
            "explanation": explanation
        }

    @staticmethod
    def analyze_key2_angulation(
        landmarks: Dict[str, Tuple[float, float]],
        segmented_teeth: Dict[int, Dict[str, Any]],
        v_op_norm: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Key 2: Crown Angulation (Tip).
        Evaluates crown axial tipping relative to perpendicular of the occlusal plane.
        """
        if not segmented_teeth:
            return {
                "key": "Key 2: Crown Angulation",
                "status": "Measurement Unavailable",
                "score": None,
                "angulations": {},
                "violations": [],
                "explanation": "No segmented teeth available for crown angulation analysis."
            }

        violations = []
        scores = []
        angulations = {}
        
        for fdi, tooth in segmented_teeth.items():
            mid = tooth.get("centroid") or landmarks.get(f"{fdi}_midpoint")
            inc = landmarks.get(f"{fdi}_incisal_edge") or landmarks.get(f"{fdi}_cusp_tip")
            
            if not mid or not inc:
                continue
                
            is_upper = (fdi < 30)
            v_axis = (inc[0] - mid[0], inc[1] - mid[1]) if is_upper else (mid[0] - inc[0], mid[1] - inc[1])
            op_angle = calculate_angle_between_vectors(v_axis, v_op_norm)
            tip_val = 90.0 - op_angle
            
            quadrant = fdi // 10
            if quadrant in [2, 3]:
                tip_val = -tip_val
                
            angulations[fdi] = round(tip_val, 1)
            ideal = AndrewsSixKeysAnalyzer.IDEAL_TIP.get(fdi, 5.0)
            dev = abs(tip_val - ideal)
            
            tooth_score = max(0.0, 1.0 - (dev / 10.0))
            scores.append(tooth_score)
            
            if dev > 4.0:
                severity = "Mild" if dev <= 6.0 else "Moderate" if dev <= 9.0 else "Severe"
                violations.append({
                    "tooth": fdi,
                    "angulation": round(tip_val, 1),
                    "ideal": ideal,
                    "deviation": round(dev, 1),
                    "severity": severity,
                    "explanation": f"Tooth {fdi} angulation is {round(tip_val, 1)}°, deviating by {round(dev, 1)}° from ideal Andrews standard ({ideal}°)."
                })
                
        if scores:
            avg_score = sum(scores) / len(scores)
            status = "Acceptable Crown Angulations" if avg_score > 0.8 else "Tipping Violations Detected"
            explanation = f"Angulation score is {round(avg_score*100, 1)}%. Found {len(violations)} teeth with tipping deviations."
        else:
            avg_score = None
            status = "Insufficient Landmarks"
            explanation = "Insufficient landmark keypoints to compute crown angulations."
            
        return {
            "key": "Key 2: Crown Angulation",
            "status": status,
            "score": round(avg_score, 2) if avg_score is not None else None,
            "angulations": angulations,
            "violations": violations,
            "explanation": explanation
        }

    @staticmethod
    def analyze_key3_inclination(view_type: str = "frontal") -> Dict[str, Any]:
        """
        Key 3: Crown Inclination (Torque).
        Clinically guarded: 3rd-order labiolingual torque cannot be derived from a 2D frontal photograph.
        """
        return {
            "key": "Key 3: Crown Inclination (Torque)",
            "status": "Unavailable on 2D Photography",
            "score": None,
            "torques": {},
            "violations": [],
            "explanation": "Labiolingual crown torque represents 3rd-order movement perpendicular to the coronal plane. Diagnostic measurement requires 3D digital study casts or lateral cephalometry."
        }

    @staticmethod
    def analyze_key4_rotations(
        segmented_teeth: Dict[int, Dict[str, Any]],
        view_type: str = "frontal"
    ) -> Dict[str, Any]:
        """
        Key 4: Rotations (Absence of rotations).
        Computed on occlusal arch views or intraoral frontal segments.
        """
        if not segmented_teeth:
            return {
                "key": "Key 4: Absence of Rotations",
                "status": "Measurement Unavailable",
                "score": None,
                "rotations": {},
                "violations": [],
                "explanation": "No segmented teeth detected to evaluate tooth rotations."
            }

        violations = []
        scores = []
        rotations = {}
        
        for fdi, tooth in segmented_teeth.items():
            bbox = tooth["bbox"]
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            if h <= 0:
                continue
                
            aspect = w / h
            ideal_aspect = 0.75 if tooth["class"] in ["incisor", "canine"] else 0.95
            dev_aspect = abs(aspect - ideal_aspect)
            
            # Clinical threshold: significant deviations in horizontal profile imply axial rotation
            if dev_aspect > 0.20:
                rot_deg = min(40.0, dev_aspect * 60.0)
                rotations[fdi] = round(rot_deg, 1)
                severity = "Mild" if rot_deg <= 12.0 else "Moderate" if rot_deg <= 22.0 else "Severe"
                violations.append({
                    "tooth": fdi,
                    "rotation_deg": round(rot_deg, 1),
                    "severity": severity,
                    "explanation": f"Tooth {fdi} exhibits contour symmetry deviation indicating possible rotation (~{round(rot_deg, 1)}°)."
                })
                scores.append(max(0.0, 1.0 - (rot_deg / 25.0)))
            else:
                rotations[fdi] = 0.0
                scores.append(1.0)
                
        avg_score = sum(scores) / len(scores) if scores else 1.0
        status = "No Significant Rotations" if avg_score > 0.85 else "Tooth Rotations Detected"
        
        return {
            "key": "Key 4: Absence of Rotations",
            "status": status,
            "score": round(avg_score, 2),
            "rotations": rotations,
            "violations": violations,
            "explanation": f"Rotation assessment score: {round(avg_score*100, 1)}%. Found {len(violations)} teeth with rotational discrepancies."
        }

    @staticmethod
    def analyze_key5_contacts(
        segmented_teeth: Dict[int, Dict[str, Any]],
        scale_factor: float
    ) -> Dict[str, Any]:
        """
        Key 5: Tight Interproximal Contacts (Absence of spacing/crowding).
        """
        if len(segmented_teeth) < 2:
            return {
                "key": "Key 5: Spacing and Contacts",
                "status": "Measurement Unavailable",
                "score": None,
                "gaps_mm": {},
                "violations": [],
                "explanation": "Insufficient adjacent tooth segments detected to evaluate interproximal contacts."
            }

        violations = []
        scores = []
        gaps = {}
        
        upper_teeth = sorted([t for t in segmented_teeth.keys() if t < 30])
        lower_teeth = sorted([t for t in segmented_teeth.keys() if t >= 30])
        
        def check_gap(t1, t2):
            box1 = segmented_teeth[t1]["bbox"]
            box2 = segmented_teeth[t2]["bbox"]
            gap_norm = box2[0] - box1[2]
            return round(gap_norm * scale_factor, 2)
            
        for t_list, arch_name in [(upper_teeth, "upper"), (lower_teeth, "lower")]:
            for i in range(len(t_list) - 1):
                t1, t2 = t_list[i], t_list[i+1]
                gap_val = check_gap(t1, t2)
                gaps[f"{t1}-{t2}"] = gap_val
                
                if gap_val > 1.8: # Spacing
                    dev = round(gap_val, 1)
                    severity = "Mild" if dev <= 2.5 else "Moderate" if dev <= 4.0 else "Severe"
                    violations.append({
                        "teeth": (t1, t2),
                        "type": "Spacing",
                        "deviation_mm": dev,
                        "severity": severity,
                        "explanation": f"Spacing gap of {dev} mm detected between {arch_name} teeth {t1} and {t2}."
                    })
                    scores.append(max(0.2, 1.0 - (dev / 6.0)))
                elif gap_val < -1.8: # Crowding
                    dev = round(abs(gap_val), 1)
                    severity = "Mild" if dev <= 2.5 else "Moderate" if dev <= 4.0 else "Severe"
                    violations.append({
                        "teeth": (t1, t2),
                        "type": "Crowding",
                        "deviation_mm": dev,
                        "severity": severity,
                        "explanation": f"Crowding overlap of {dev} mm detected between {arch_name} teeth {t1} and {t2}."
                    })
                    scores.append(max(0.2, 1.0 - (dev / 6.0)))
                else:
                    scores.append(1.0)
                    
        avg_score = sum(scores) / len(scores) if scores else 1.0
        status = "Tight Interproximal Contacts" if avg_score > 0.8 else "Contact Deviations Present"
        
        return {
            "key": "Key 5: Spacing and Contacts",
            "status": status,
            "score": round(avg_score, 2),
            "gaps_mm": gaps,
            "violations": violations,
            "explanation": f"Contact score is {round(avg_score*100, 1)}%. Found {len(violations)} spacing/crowding violations."
        }

    @staticmethod
    def analyze_key6_spee(
        landmarks: Dict[str, Tuple[float, float]],
        v_op_norm: Tuple[float, float],
        scale_factor: float,
        view_type: str = "frontal"
    ) -> Dict[str, Any]:
        """
        Key 6: Curve of Spee.
        Only clinically applicable on Lateral and Panoramic views.
        """
        if view_type in ["frontal", "occlusal_upper", "occlusal_lower"]:
            return {
                "key": "Key 6: Curve of Spee",
                "status": "Unavailable for Frontal View",
                "score": None,
                "depth_mm": None,
                "explanation": "Curve of Spee represents the sagittal curvature of the mandibular occlusal plane. It can only be diagnosed on lateral profile views or panoramic radiographs."
            }

        li = landmarks.get("31_incisal_edge") or landmarks.get("41_incisal_edge")
        lm = landmarks.get("37_cusp_tip_buccal") or landmarks.get("47_cusp_tip_buccal") or landmarks.get("36_buccal_groove") or landmarks.get("46_buccal_groove")
        
        if not li or not lm:
            return {
                "key": "Key 6: Curve of Spee",
                "status": "Measurement Unavailable",
                "score": None,
                "depth_mm": None,
                "explanation": "Incisal or molar landmark coordinates not detectable on this sagittal radiograph."
            }
            
        m = (lm[1] - li[1]) / (lm[0] - li[0]) if (lm[0] - li[0]) != 0 else 0
        deepest_depth_norm = 0.0
        for fdi in [34, 35, 36, 44, 45, 46]:
            cusp = landmarks.get(f"{fdi}_cusp_tip_buccal")
            if cusp:
                line_y_at_cusp = m * cusp[0] + (li[1] - m * li[0])
                depth_norm = cusp[1] - line_y_at_cusp
                if depth_norm > deepest_depth_norm:
                    deepest_depth_norm = depth_norm
                    
        depth_mm = deepest_depth_norm * scale_factor
        if depth_mm <= 1.5:
            status = "Flat (Normal)"
            score = 1.0
            explanation = f"Curve of Spee is flat and optimal ({round(depth_mm, 1)} mm), matching standard orthodontic finishing criteria."
        elif depth_mm <= 3.0:
            status = "Mildly Deep Curve of Spee"
            score = 0.8
            explanation = f"Mildly deep Curve of Spee ({round(depth_mm, 1)} mm). Leveling of mandibular arch indicated."
        else:
            status = "Excessive Deep Curve of Spee"
            score = 0.5
            explanation = f"Severe Curve of Spee depth ({round(depth_mm, 1)} mm). Intrusion of lower incisors or premolar leveling recommended."
            
        return {
            "key": "Key 6: Curve of Spee",
            "status": status,
            "score": round(score, 2),
            "depth_mm": round(depth_mm, 2),
            "explanation": explanation
        }

    @staticmethod
    def run_full_analysis(
        landmarks: Dict[str, Tuple[float, float]],
        segmented_teeth: Dict[int, Dict[str, Any]],
        v_op_norm: Tuple[float, float],
        scale_factor: float,
        view_type: str = "frontal"
    ) -> Dict[str, Any]:
        """
        Executes analysis across all Six Keys with strict view guarding.
        Calculates overall score strictly from available, applicable keys.
        """
        k1 = AndrewsSixKeysAnalyzer.analyze_key1_molar(landmarks, v_op_norm, scale_factor)
        k2 = AndrewsSixKeysAnalyzer.analyze_key2_angulation(landmarks, segmented_teeth, v_op_norm)
        k3 = AndrewsSixKeysAnalyzer.analyze_key3_inclination(view_type=view_type)
        k4 = AndrewsSixKeysAnalyzer.analyze_key4_rotations(segmented_teeth, view_type=view_type)
        k5 = AndrewsSixKeysAnalyzer.analyze_key5_contacts(segmented_teeth, scale_factor)
        k6 = AndrewsSixKeysAnalyzer.analyze_key6_spee(landmarks, v_op_norm, scale_factor, view_type=view_type)
        
        keys = [k1, k2, k3, k4, k5, k6]
        valid_scores = [k["score"] for k in keys if k["score"] is not None]
        overall_score = (sum(valid_scores) / len(valid_scores) * 100.0) if valid_scores else 0.0
        
        return {
            "overall_andrews_score": round(overall_score, 1),
            "applicable_keys_count": len(valid_scores),
            "details": keys
        }
