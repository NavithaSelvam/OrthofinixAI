import sys
import os
import hashlib
import io
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_engine import OrthodonticAIEngine

def create_image_A():
    """
    Image A: Well-aligned, symmetrical clinical dentition.
    Upper and lower arches are centered and symmetrical.
    """
    img = Image.new("RGB", (640, 480), color=(170, 70, 80)) # gingival oral background
    draw = ImageDraw.Draw(img)
    # Upper arch teeth (symmetric around center X=320)
    upper_x = [140, 180, 220, 260, 300, 340, 380, 420, 460, 500]
    for x in upper_x:
        draw.rounded_rectangle([x - 16, 160, x + 16, 235], radius=5, fill=(245, 245, 235), outline=(140, 140, 140))
    # Lower arch teeth (symmetric around center X=320)
    lower_x = [150, 190, 230, 270, 305, 335, 370, 410, 450, 490]
    for x in lower_x:
        draw.rounded_rectangle([x - 14, 250, x + 14, 315], radius=5, fill=(240, 240, 230), outline=(140, 140, 140))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def create_image_B():
    """
    Image B: Severely crowded, asymmetric clinical dentition with severe midline shift.
    Upper teeth are vertically staggered/tilted and lower arch is shifted to the right.
    """
    img = Image.new("RGB", (640, 480), color=(140, 55, 65)) # darker gingival background
    draw = ImageDraw.Draw(img)
    # Upper arch with severe vertical step discrepancies and irregular spacing
    upper_x = [120, 165, 195, 240, 290, 370, 410, 465, 505, 545]
    upper_y = [175, 145, 185, 140, 180, 150, 190, 155, 175, 150]
    for x, y in zip(upper_x, upper_y):
        draw.rounded_rectangle([x - 18, y, x + 18, y + 80], radius=8, fill=(230, 225, 215), outline=(90, 90, 90))
    # Lower arch shifted far to the right (severe midline deviation)
    lower_x = [180, 225, 265, 315, 355, 405, 455, 495, 535]
    lower_y = [265, 245, 275, 250, 270, 245, 265, 250, 270]
    for x, y in zip(lower_x, lower_y):
        draw.rounded_rectangle([x - 15, y, x + 15, y + 68], radius=5, fill=(225, 220, 210), outline=(90, 90, 90))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def run_sensitivity_audit():
    print("=" * 80)
    print("CLINICAL AI PIPELINE SENSITIVITY AUDIT (IMAGE A vs IMAGE B)")
    print("=" * 80)

    bytes_A = create_image_A()
    bytes_B = create_image_B()

    hash_A = hashlib.sha256(bytes_A).hexdigest()[:16]
    hash_B = hashlib.sha256(bytes_B).hexdigest()[:16]

    print(f"\n[1] IMAGE HASHES:")
    print(f"  Image A Hash: {hash_A} (Bytes: {len(bytes_A)})")
    print(f"  Image B Hash: {hash_B} (Bytes: {len(bytes_B)})")

    engine = OrthodonticAIEngine()

    print("\n[2] RUNNING INFERENCE ON IMAGE A (Symmetric Dentition)...")
    res_A = engine.analyze_image(bytes_A, view_type="frontal")

    print("\n[3] RUNNING INFERENCE ON IMAGE B (Crowded / Asymmetric Dentition)...")
    res_B = engine.analyze_image(bytes_B, view_type="frontal")

    print("\n" + "=" * 80)
    print("STAGE-BY-STAGE SENSITIVITY COMPARISON")
    print("=" * 80)

    # 1. Detected Teeth Count & FDI
    teeth_A = res_A["details"]["segmented_teeth"]
    teeth_B = res_B["details"]["segmented_teeth"]
    print(f"  A. Detected Teeth Count : Image A = {len(teeth_A)} | Image B = {len(teeth_B)}")
    print(f"     Image A FDIs         : {teeth_A}")
    print(f"     Image B FDIs         : {teeth_B}")

    # 2. Keypoints / Landmarks
    lm_A = res_A["details"]["detected_landmarks"]
    lm_B = res_B["details"]["detected_landmarks"]
    print(f"\n  B. Landmark Coordinates:")
    sample_key = "11_incisal_edge" if "11_incisal_edge" in lm_A else list(lm_A.keys())[0]
    print(f"     Sample Point '{sample_key}': Image A = {lm_A.get(sample_key)} | Image B = {lm_B.get(sample_key)}")
    print(f"     Total Landmarks Count: Image A = {len(lm_A)} | Image B = {len(lm_B)}")

    # 3. Clinical Measurements
    mv_A = res_A["measured_values"]
    mv_B = res_B["measured_values"]
    print(f"\n  C. Clinical Measurements:")
    print(f"     Midline Deviation (mm): Image A = {mv_A.get('midline_deviation_mm')} mm | Image B = {mv_B.get('midline_deviation_mm')} mm")
    print(f"     Overjet (mm)          : Image A = {mv_A.get('overjet_mm')} mm | Image B = {mv_B.get('overjet_mm')} mm")
    print(f"     Occlusal Slope        : Image A = {mv_A.get('occlusal_plane', {}).get('slope')} | Image B = {mv_B.get('occlusal_plane', {}).get('slope')}")

    # 4. Clinical Scores
    print(f"\n  D. Clinical Scores:")
    print(f"     Finishing Score (%)   : Image A = {res_A['finishing_score']}% | Image B = {res_B['finishing_score']}%")
    print(f"     Arch Symmetry Score   : Image A = {res_A['arch_symmetry_score']}% | Image B = {res_B['arch_symmetry_score']}%")
    print(f"     Andrews Score         : Image A = {res_A['andrews_score']}% | Image B = {res_B['andrews_score']}%")
    print(f"     ABO Deductions        : Image A = {res_A['abo_score']} pts | Image B = {res_B['abo_score']} pts")

    # 5. Recommendations
    print(f"\n  E. Recommendations Generated:")
    print(f"     Image A Recommendations ({len(res_A['recommendations'])}):")
    for r in res_A['recommendations']:
        print(f"       - {r}")
    print(f"     Image B Recommendations ({len(res_B['recommendations'])}):")
    for r in res_B['recommendations']:
        print(f"       - {r}")

    # 6. Sensitivity Validation Check
    is_different = (
        (res_A["finishing_score"] != res_B["finishing_score"]) and
        (res_A["arch_symmetry_score"] != res_B["arch_symmetry_score"]) and
        (mv_A["midline_deviation_mm"] != mv_B["midline_deviation_mm"]) and
        (teeth_A != teeth_B or lm_A != lm_B)
    )

    print("\n" + "=" * 80)
    if is_different:
        print("SENSITIVITY TEST RESULT: PASS (Model output is demonstrably dependent on uploaded image)")
    else:
        print("SENSITIVITY TEST RESULT: FAIL (Outputs are identical or non-responsive)")
    print("=" * 80)

if __name__ == "__main__":
    run_sensitivity_audit()
