import json
from app.db.firebase import init_firebase, save_analysis_record
from app.services.ai_engine import ai_engine
import numpy as np

def debug():
    # Load dummy/test image bytes
    with open("uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg", "rb") as f:
        image_bytes = f.read()
        
    result = ai_engine.analyze_image(image_bytes, view_type="frontal")
    
    case_data = {
        "patient_name": "Test Patient",
        "image_url": "https://example.com/test.jpg",
        "view_type": "frontal",
        "status": "completed",
        "finishing_score": 80.0,
        "alignment_score": 80.0,
        "confidence_score": 0.8,
        "midline_deviation_mm": 2.0,
        "overjet_mm": 2.0,
        "overbite_percent": 30.0,
        "abo_score": 10.0,
        "andrews_score": 80.0,
        "root_angulation_score": 80.0,
        "prediction": result.get("prediction", ""),
        "recommendations": result.get("recommendations", []),
        "metrics": result.get("details", {}),
        "created_at": None
    }
    
    safe_data = json.loads(json.dumps(case_data))
    
    # Print type analysis of safe_data
    print("ANALYZING safe_data TYPES:")
    def print_types(d, indent=0):
        if isinstance(d, dict):
            for k, v in d.items():
                print("  " * indent + f"{k} ({type(k).__name__}): {type(v).__name__}")
                if isinstance(v, (dict, list)):
                    print_types(v, indent + 1)
        elif isinstance(d, list):
            print("  " * indent + f"LIST (len={len(d)}) of {type(d[0]).__name__ if d else 'empty'}")
            if d and isinstance(d[0], (dict, list)):
                print_types(d[0], indent + 1)
                
    print_types(safe_data)

if __name__ == "__main__":
    debug()
