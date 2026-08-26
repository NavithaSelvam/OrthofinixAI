from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from firebase_admin import auth

from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import User
bearer_scheme = HTTPBearer(auto_error=False)



def get_current_summit_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db_session),
) -> User:

    print("Authorization:", credentials)

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="No Authorization header"
        )

    try:
        payload = auth.verify_id_token(credentials.credentials)
        print(payload)
    except Exception as e:
        print("VERIFY ERROR:", e)
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

    uid = payload["uid"]
    email = payload.get("email", "")
    name = payload.get("name", "")

    # Check whether the user already exists by Firebase UID
    user = db.query(User).filter(User.id == uid).first()
    if user:
        if email and user.email != email:
            user.email = email
            db.commit()
        return user

    # Check whether a user with the same email already exists (e.g. legacy seed)
    if email:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            # Update existing row's ID to match the authoritative Firebase UID
            existing_user.id = uid
            db.commit()
            return existing_user

    # Create a new Firebase-authenticated user with exact UID
    user = User(
        id=uid,
        email=email if email else f"{uid}@orthofinix.ai",
        password_hash=None,
        display_name=name if name else "Doctor",
        role="doctor"
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return user