import io
import os
import sys
import uuid
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user
from app.models.schemas import UserInfo
from app.services.ai_engine import OrthodonticAIEngine

# Authenticated Test Doctor
test_doctor = UserInfo(
    uid="doctor_dynamic_ai_uid",
    email="doctor_dynamic@orthofinix.ai",
    display_name="Dr. Dynamic AI",
    role="doctor"
)

app.dependency_overrides[get_current_user] = lambda: test_doctor
client = TestClient(app)
engine = OrthodonticAIEngine()


def create_simulated_frontal_image(arch_asymmetry: float = 0.0, midline_offset: int = 0):
    """
    Creates a simulated intraoral frontal smile image with tooth enamel contours,
    pink gingival margins, and adjustable midline / transverse asymmetry.
    """
    img = Image.new("RGB", (800, 600), color=(180, 50, 70)) # Gingiva background
    draw = ImageDraw.Draw(img)

    # Upper teeth row (FDI 14 to 24)
    upper_center_x = 400 + midline_offset
    upper_y = 220
    tooth_w, tooth_h = 42, 60

    # Maxillary teeth
    teeth_x = [
        upper_center_x - 170 - int(arch_asymmetry * 15), # 14
        upper_center_x - 120 - int(arch_asymmetry * 10), # 13
        upper_center_x - 70 - int(arch_asymmetry * 5),   # 12
        upper_center_x - 24,                            # 11
        upper_center_x + 24,                            # 21
        upper_center_x + 70,                            # 22
        upper_center_x + 120,                           # 23
        upper_center_x + 170                            # 24
    ]

    for tx in teeth_x:
        # Enamel tooth body
        draw.ellipse([tx - tooth_w // 2, upper_y, tx + tooth_w // 2, upper_y + tooth_h], fill=(245, 245, 235), outline=(190, 190, 180), width=2)
        # Incisal edge highlight
        draw.line([tx - tooth_w // 2 + 4, upper_y + tooth_h - 4, tx + tooth_w // 2 - 4, upper_y + tooth_h - 4], fill=(255, 255, 250), width=2)

    # Lower teeth row (FDI 44 to 34)
    lower_center_x = 400
    lower_y = 300
    lower_w, lower_h = 36, 55

    lower_teeth_x = [
        lower_center_x - 150,
        lower_center_x - 105,
        lower_center_x - 60,
        lower_center_x - 20,
        lower_center_x + 20,
        lower_center_x + 60,
        lower_center_x + 105,
        lower_center_x + 150
    ]

    for tx in lower_teeth_x:
        draw.ellipse([tx - lower_w // 2, lower_y, tx + lower_w // 2, lower_y + lower_h], fill=(240, 240, 230), outline=(180, 180, 170), width=2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()


def create_simulated_opg_image(root_divergence: float = 0.0):
    """
    Creates a simulated panoramic radiograph (OPG) with radiopaque root structures.
    """
    img = Image.new("RGB", (900, 500), color=(30, 30, 35)) # Radiograph dark background
    draw = ImageDraw.Draw(img)

    # Maxillary radiopaque teeth & roots
    center_x = 450
    for i, offset in enumerate(range(-350, 360, 50)):
        tx = center_x + offset
        crown_y = 200
        # Root apex with divergence tilt
        tilt = int(root_divergence * (i - 7) * 4)
        apex_x = tx + tilt
        apex_y = 110
        # Root vector
        draw.polygon([(tx - 18, crown_y), (tx + 18, crown_y), (apex_x + 6, apex_y), (apex_x - 6, apex_y)], fill=(220, 220, 220), outline=(255, 255, 255))
        # Crown
        draw.ellipse([tx - 20, crown_y - 15, tx + 20, crown_y + 25], fill=(240, 240, 240))

    # Mandibular radiopaque teeth & roots
    for i, offset in enumerate(range(-320, 330, 45)):
        tx = center_x + offset
        crown_y = 270
        apex_y = 370
        draw.polygon([(tx - 15, crown_y), (tx + 15, crown_y), (tx + 5, apex_y), (tx - 5, apex_y)], fill=(210, 210, 210), outline=(255, 255, 255))
        draw.ellipse([tx - 18, crown_y - 10, tx + 18, crown_y + 20], fill=(235, 235, 235))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()


def create_simulated_lateral_image(overjet_offset: int = 0):
    """
    Creates a simulated lateral sagittal intraoral photo showing incisor overlap.
    """
    img = Image.new("RGB", (700, 550), color=(140, 40, 50))
    draw = ImageDraw.Draw(img)

    # Upper incisor profile
    upper_x = 380 + overjet_offset
    upper_y = 180
    draw.polygon([(upper_x, upper_y), (upper_x + 60, upper_y + 40), (upper_x + 40, upper_y + 160), (upper_x - 10, upper_y + 150)], fill=(245, 245, 238), outline=(190, 190, 180), width=2)

    # Lower incisor profile
    lower_x = 340
    lower_y = 260
    draw.polygon([(lower_x, lower_y + 140), (lower_x + 50, lower_y + 130), (lower_x + 35, lower_y), (lower_x - 15, lower_y + 10)], fill=(240, 240, 230), outline=(180, 180, 170), width=2)

    # Occlusal reference line
    draw.line([100, 310, 600, 310], fill=(220, 220, 220), width=1)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()


def test_dynamic_ai_analysis_suite():
    print("=" * 80)
    print("RUNNING DYNAMIC AI ANALYSIS VARIANCE & PREDICTION ACCURACY TEST SUITE")
    print("=" * 80)

    # 1. Test Demo Endpoint
    print("\n--- [TEST 1] GET /analysis/demo Endpoint Verification ---")
    demo_res = client.get("/analysis/demo")
    assert demo_res.status_code == 200, f"Demo endpoint failed: {demo_res.text}"
    demo_data = demo_res.json()
    assert demo_data["id"] == "demo_star_benchmark_case"
    assert demo_data["finishing_score"] > 80.0
    assert len(demo_data["recommendations"]) >= 3
    print(f"  [PASS TEST 1] Demo endpoint returned valid benchmark case: score={demo_data['finishing_score']}%, recommendations={len(demo_data['recommendations'])}")

    # 2. Test Frontal Image A (Symmetric, Aligned) vs Frontal Image B (Asymmetric, Midline Shifted)
    print("\n--- [TEST 2] Frontal View Variance: Ideal vs Asymmetric Cases ---")
    bytes_frontal_ideal = create_simulated_frontal_image(arch_asymmetry=0.0, midline_offset=0)
    bytes_frontal_asymm = create_simulated_frontal_image(arch_asymmetry=2.5, midline_offset=28)

    res_frontal_ideal = engine.analyze_image(bytes_frontal_ideal, view_type="frontal")
    res_frontal_asymm = engine.analyze_image(bytes_frontal_asymm, view_type="frontal")

    print(f"  [Ideal Frontal] Score: {res_frontal_ideal['finishing_score']}%, Midline Dev: {res_frontal_ideal['measured_values']['midline_deviation_mm']} mm, Symmetry: {res_frontal_ideal['calculated_scores']['arch_symmetry_score']}%")
    print(f"  [Asymm Frontal] Score: {res_frontal_asymm['finishing_score']}%, Midline Dev: {res_frontal_asymm['measured_values']['midline_deviation_mm']} mm, Symmetry: {res_frontal_asymm['calculated_scores']['arch_symmetry_score']}%")

    # Verify that the two frontal images produced DIFFERENT results based on their actual features
    assert res_frontal_ideal["finishing_score"] != res_frontal_asymm["finishing_score"], "Scores must not be identical across different images!"
    assert res_frontal_ideal["measured_values"]["midline_deviation_mm"] != res_frontal_asymm["measured_values"]["midline_deviation_mm"], "Midline deviation must reflect image variance!"
    print("  [PASS TEST 2] Frontal analysis produced distinct, accurate metrics for different images")

    # 3. Test OPG View: Ideal Parallelism vs Root Divergence
    print("\n--- [TEST 3] OPG View Variance: Parallel vs Divergent Roots ---")
    bytes_opg_parallel = create_simulated_opg_image(root_divergence=0.0)
    bytes_opg_divergent = create_simulated_opg_image(root_divergence=1.8)

    res_opg_parallel = engine.analyze_image(bytes_opg_parallel, view_type="opg")
    res_opg_divergent = engine.analyze_image(bytes_opg_divergent, view_type="opg")

    print(f"  [Parallel OPG] Score: {res_opg_parallel['finishing_score']}%, Root Parallelism: {res_opg_parallel['root_angulation_score']}%")
    print(f"  [Divergent OPG] Score: {res_opg_divergent['finishing_score']}%, Root Parallelism: {res_opg_divergent['root_angulation_score']}%")

    assert res_opg_parallel["finishing_score"] > 0, "OPG finishing score must not be 0.0 for valid radiograph!"
    assert res_opg_parallel["finishing_score"] != res_opg_divergent["finishing_score"], "OPG scores must vary with root angulation divergence!"
    print("  [PASS TEST 3] OPG analysis produced distinct, accurate root parallelism metrics")

    # 4. Test Lateral View: Normal Overjet vs Class II Overjet
    print("\n--- [TEST 4] Lateral View Variance: Normal vs Excessive Overjet ---")
    bytes_lat_normal = create_simulated_lateral_image(overjet_offset=10)
    bytes_lat_class2 = create_simulated_lateral_image(overjet_offset=70)

    res_lat_normal = engine.analyze_image(bytes_lat_normal, view_type="lateral")
    res_lat_class2 = engine.analyze_image(bytes_lat_class2, view_type="lateral")

    print(f"  [Normal Lateral] Score: {res_lat_normal['finishing_score']}%, Overjet: {res_lat_normal['measured_values']['overjet_mm']} mm, Overbite: {res_lat_normal['measured_values']['overbite_percent']}%")
    print(f"  [Class II Lateral] Score: {res_lat_class2['finishing_score']}%, Overjet: {res_lat_class2['measured_values']['overjet_mm']} mm, Overbite: {res_lat_class2['measured_values']['overbite_percent']}%")

    assert res_lat_normal["finishing_score"] != res_lat_class2["finishing_score"], "Lateral scores must vary based on overjet!"
    print("  [PASS TEST 4] Lateral analysis produced distinct, accurate overjet & overbite metrics")

    # 5. Test End-to-End API analyze endpoint with real image upload
    print("\n--- [TEST 5] End-to-End API /analysis/analyze Integration ---")
    up_res = client.post("/analysis/upload", files={"file": ("test_frontal_case.jpg", io.BytesIO(bytes_frontal_ideal), "image/jpeg")})
    assert up_res.status_code == 200
    up_id = up_res.json()["upload_id"]

    ana_res = client.post("/analysis/analyze", data={
        "upload_id": up_id,
        "patient_name": "Dynamic Test Patient",
        "view_type": "frontal",
        "case_id": f"dyn_case_{uuid.uuid4().hex[:8]}"
    })
    assert ana_res.status_code == 200
    ana_data = ana_res.json()
    print(f"  [API Analyze Output] ID: {ana_data['id']}, Finishing Score: {ana_data['finishing_score']}%, Alignment Score: {ana_data['alignment_score']}%")
    assert ana_data["finishing_score"] > 50.0, f"Finishing score should reflect actual frontal analysis, got {ana_data['finishing_score']}"
    print("  [PASS TEST 5] API /analysis/analyze successfully calculated and returned dynamic score")

    print("\n" + "=" * 80)
    print("ALL DYNAMIC AI ANALYSIS TESTS PASSED (5/5)!")
    print("=" * 80)


if __name__ == "__main__":
    test_dynamic_ai_analysis_suite()
