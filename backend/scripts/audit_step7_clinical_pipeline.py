import os
import sys
import numpy as np
import cv2
import json
import onnxruntime as ort

# Add backend to path
sys.path.insert(0, os.path.abspath("backend"))

from app.services.ai_engine import OrthodonticAIEngine
from app.services.ai_models.clinical_analysis.segmentation import ToothSegmentationModel
from app.services.ai_models.clinical_analysis.landmarks import LandmarkDetectionModel
from app.services.ai_models.clinical_analysis.opg_model import OPGLandmarkModel
from app.services.ai_models.clinical_analysis.andrews_keys import AndrewsSixKeysAnalyzer
from app.services.ai_models.clinical_analysis.overjet_overbite import OverjetOverbiteAnalyzer
from app.services.ai_models.clinical_analysis.opg_uprighting import OPGUprightingAnalyzer

print("=" * 80)
print("STEP 7: COMPREHENSIVE CLINICAL AI PIPELINE EXECUTION AUDIT")
print("=" * 80)

engine = OrthodonticAIEngine()

# 1. Weights Inspection
weights_dir = "backend/app/services/ai_models/weights"
for model_file in ["ortho_seg_v1.onnx", "ortho_landmarks_v1.onnx", "ortho_opg_v1.onnx"]:
    path = os.path.join(weights_dir, model_file)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
    inputs = [f"{i.name}: {i.shape} ({i.type})" for i in sess.get_inputs()]
    outputs = [f"{o.name}: {o.shape} ({o.type})" for o in sess.get_outputs()]
    print(f"\nModel File: {model_file} (Size: {size} bytes)")
    print(f"  Inputs:  {inputs}")
    print(f"  Outputs: {outputs}")

# 2. Generate two distinct synthetic clinical test images (Sample A: Normal Occlusion, Sample B: Asymmetric Class II with deep bite)
# Image A: Normal symmetric arch with teeth positioned at standard coords
img_a = np.full((600, 800, 3), (220, 200, 190), dtype=np.uint8) # oral background
cv2.ellipse(img_a, (400, 320), (220, 120), 0, 0, 180, (245, 245, 240), -1) # dental arch
cv2.ellipse(img_a, (400, 320), (180, 80), 0, 0, 180, (140, 60, 60), -1) # inner oral cavity
# Draw distinct teeth on Image A
for x_offset in range(220, 580, 28):
    cv2.rectangle(img_a, (x_offset, 270), (x_offset + 24, 330), (250, 250, 245), -1)
    cv2.rectangle(img_a, (x_offset, 270), (x_offset + 24, 330), (180, 170, 160), 1)

# Image B: Severe crowding, tilted occlusal plane, asymmetric arch
img_b = np.full((600, 800, 3), (200, 180, 170), dtype=np.uint8)
cv2.ellipse(img_b, (440, 350), (260, 140), 12, 0, 180, (240, 240, 235), -1) # tilted arch
cv2.ellipse(img_b, (440, 350), (200, 90), 12, 0, 180, (120, 40, 40), -1)
# Draw staggered/crowded teeth on Image B
for idx, x_offset in enumerate(range(200, 620, 30)):
    y_shift = int(np.sin(idx) * 25)
    cv2.rectangle(img_b, (x_offset, 260 + y_shift), (x_offset + 26, 320 + y_shift), (250, 250, 245), -1)
    cv2.rectangle(img_b, (x_offset, 260 + y_shift), (x_offset + 26, 320 + y_shift), (160, 150, 140), 1)

# Encode to JPEG bytes
_, buf_a = cv2.imencode(".jpg", img_a)
_, buf_b = cv2.imencode(".jpg", img_b)

bytes_a = buf_a.tobytes()
bytes_b = buf_b.tobytes()

print("\n" + "-" * 80)
print("TRACE: EXECUTING FULL PIPELINE ON SAMPLE IMAGE A (Frontal View)")
print("-" * 80)
res_a = engine.analyze_image(bytes_a, view_type="frontal")

print(f"Status: {res_a.get('status')}")
print(f"Finishing Score: {res_a.get('finishing_score')}%")
print(f"Andrews Score: {res_a.get('andrews_score')}%")
print(f"Arch Symmetry Score: {res_a.get('arch_symmetry_score')}%")
print(f"ABO Score (Deductions): {res_a.get('abo_score')}")
print(f"Overjet (mm): {res_a.get('measured_values', {}).get('overjet_mm')}")
print(f"Overbite (%): {res_a.get('measured_values', {}).get('overbite_percent')}")
print(f"Midline Deviation (mm): {res_a.get('measured_values', {}).get('midline_deviation_mm')}")
print(f"Teeth Detected: {res_a.get('measured_values', {}).get('detected_teeth_count')}")
print(f"Inference Time: {res_a.get('model_metadata', {}).get('inference_time_ms')} ms")
print(f"Recommendations:\n  " + "\n  ".join(res_a.get('recommendations', [])))

print("\n" + "-" * 80)
print("TRACE: EXECUTING FULL PIPELINE ON SAMPLE IMAGE B (Crowded/Asymmetric View)")
print("-" * 80)
res_b = engine.analyze_image(bytes_b, view_type="frontal")

print(f"Status: {res_b.get('status')}")
print(f"Finishing Score: {res_b.get('finishing_score')}%")
print(f"Andrews Score: {res_b.get('andrews_score')}%")
print(f"Arch Symmetry Score: {res_b.get('arch_symmetry_score')}%")
print(f"ABO Score (Deductions): {res_b.get('abo_score')}")
print(f"Overjet (mm): {res_b.get('measured_values', {}).get('overjet_mm')}")
print(f"Overbite (%): {res_b.get('measured_values', {}).get('overbite_percent')}")
print(f"Midline Deviation (mm): {res_b.get('measured_values', {}).get('midline_deviation_mm')}")
print(f"Teeth Detected: {res_b.get('measured_values', {}).get('detected_teeth_count')}")
print(f"Inference Time: {res_b.get('model_metadata', {}).get('inference_time_ms')} ms")

print("\n" + "=" * 80)
print("IMAGE FEATURE SENSITIVITY VERIFICATION")
print("=" * 80)
print(f"Finishing Score Diff (A vs B): {abs(res_a.get('finishing_score', 0) - res_b.get('finishing_score', 0)):.2f}%")
print(f"Symmetry Score Diff (A vs B): {abs(res_a.get('arch_symmetry_score', 0) - res_b.get('arch_symmetry_score', 0)):.2f}%")
print(f"ABO Deductions Diff (A vs B): {abs(res_a.get('abo_score', 0) - res_b.get('abo_score', 0)):.2f}")
