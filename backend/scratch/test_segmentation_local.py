import cv2
import os
from app.services.ai_models.clinical_analysis.segmentation import ToothSegmentationEngine

def test_local():
    image_path = "uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg"
    if not os.path.exists(image_path):
        print("Image not found:", image_path)
        return
        
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image:", image_path)
        return
        
    engine = ToothSegmentationEngine()
    
    # Let's test with frontal view first
    res_frontal = engine.segment_image(img, view_type="frontal")
    print("Frontal segments count:", len(res_frontal))
    
    # Let's test with other view types
    for view in ["opg", "left", "right", "lateral"]:
        res = engine.segment_image(img, view_type=view)
        print(f"View {view} segments count:", len(res))

if __name__ == "__main__":
    test_local()
