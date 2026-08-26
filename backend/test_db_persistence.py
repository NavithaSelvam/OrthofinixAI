import os
import json
import uuid
from datetime import datetime, timezone

from app.db.sqlalchemy_db import init_sqlalchemy, SessionLocal, engine
from app.db.orm_models import (
    User,
    Patient,
    Case,
    UploadedImage,
    AnalysisReport,
    Post,
)

def run_tests():
    print(">>> Initializing SQLAlchemy database tables...")
    init_sqlalchemy()
    
    db = SessionLocal()
    try:
        test_uid = f"test_doctor_{uuid.uuid4().hex[:8]}"
        
        # 1. Test User creation
        print("\n1. Testing User persistence...")
        user = User(
            id=test_uid,
            email=f"{test_uid}@example.com",
            password_hash="",
            display_name="Dr. Smith Test",
            role="doctor"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   [OK] User created: id={user.id}, email={user.email}")
        
        # 2. Test Patient creation
        print("\n2. Testing Patient persistence...")
        patient_id = f"pat_{uuid.uuid4().hex[:8]}"
        patient = Patient(
            id=patient_id,
            doctor_id=user.id,
            name="John Doe",
            date_of_birth="1998-05-12",
            gender="Male",
            contact_info="555-0199"
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        print(f"   [OK] Patient created: id={patient.id}, name={patient.name}, doctor={patient.doctor.display_name}")
        
        # 3. Test Case creation
        print("\n3. Testing Case persistence...")
        case_id = f"case_{uuid.uuid4().hex[:8]}"
        case = Case(
            id=case_id,
            doctor_id=user.id,
            patient_id=patient.id,
            status="In Progress",
            notes="Initial assessment for class II malocclusion."
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        print(f"   [OK] Case created: id={case.id}, patient={case.patient.name}")
        
        # 4. Test Uploaded Image persistence
        print("\n4. Testing UploadedImage persistence...")
        image_id = f"img_{uuid.uuid4().hex[:8]}.jpg"
        upload = UploadedImage(
            id=image_id,
            user_id=user.id,
            case_id=case.id,
            filename="sample_intraoral.jpg",
            file_path=f"uploads/{image_id}",
            storage_url=f"http://127.0.0.1:8000/uploads/{image_id}",
            content_type="image/jpeg",
            view_type="frontal"
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        print(f"   [OK] UploadedImage created: id={upload.id}, url={upload.storage_url}")
        
        # 5. Test AnalysisReport persistence
        print("\n5. Testing AnalysisReport persistence...")
        report_id = f"rep_{uuid.uuid4().hex[:8]}"
        report = AnalysisReport(
            id=report_id,
            user_id=user.id,
            patient_id=patient.id,
            case_id=case.id,
            patient_name=patient.name,
            image_url=upload.storage_url,
            view_type="frontal",
            status="completed",
            finishing_score=88.5,
            alignment_score=91.0,
            confidence_score=94.2,
            midline_deviation_mm=0.8,
            overjet_mm=2.5,
            overbite_percent=25.0,
            abo_score=6.0,
            andrews_score=92.0,
            root_angulation_score=87.0,
            prediction="Optimal Class I alignment with minor tip correction needed.",
            recommendations_json=json.dumps([
                "Maintain Class I molar relation",
                "Torque adjustment on tooth 11"
            ]),
            metrics_json=json.dumps({
                "andrews_details": [{"key": "Key 1 Molar", "status": "Pass"}],
                "overjet_overbite": {"overjet_mm": 2.5, "overbite_percent": 25.0}
            })
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"   [OK] AnalysisReport created: id={report.id}, score={report.finishing_score}%, overjet={report.overjet_mm}mm")
        
        # 6. Test Post persistence
        print("\n6. Testing Post persistence...")
        post_id = f"post_{uuid.uuid4().hex[:8]}"
        post = Post(
            id=post_id,
            user_id=user.id,
            title="Finishing stage check for deep bite",
            content="Patient showed 4mm improvement in overbite after utility arch.",
            category="clinical_discussion",
            report_id=report.id
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        print(f"   [OK] Post created: id={post.id}, title='{post.title}', author='{post.author.display_name}'")
        
        # 7. Test Relationships
        print("\n7. Verifying Relationships...")
        fetched_user = db.query(User).filter(User.id == user.id).first()
        print(f"   - User has {len(fetched_user.patients)} patient(s)")
        print(f"   - User has {len(fetched_user.cases)} case(s)")
        print(f"   - User has {len(fetched_user.images)} image(s)")
        print(f"   - User has {len(fetched_user.analyses)} analysis report(s)")
        print(f"   - User has {len(fetched_user.posts)} post(s)")
        
        assert len(fetched_user.patients) >= 1
        assert len(fetched_user.cases) >= 1
        assert len(fetched_user.images) >= 1
        assert len(fetched_user.analyses) >= 1
        assert len(fetched_user.posts) >= 1
        
        print("\n ALL DATABASE PERSISTENCE TESTS PASSED SUCCESSFULLY!")
        
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
