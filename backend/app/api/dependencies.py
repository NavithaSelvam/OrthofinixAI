from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.schemas import UserInfo
from app.db.sqlalchemy_db import get_db_session
from app.db.orm_models import User
from firebase_admin import auth


security = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> UserInfo:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization Bearer token required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(
            token,
            clock_skew_seconds=10
        )

        uid = decoded.get("uid")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase UID missing from token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        email = decoded.get("email", "")
        name = decoded.get("name", "")

        # Ensure user exists in SQL database with their exact verified Firebase UID
        user_row = db.query(User).filter(User.id == uid).first()
        if not user_row:
            user_row = User(
                id=uid,
                email=email if email else f"{uid}@orthofinix.ai",
                password_hash="",
                display_name=name if name else "Doctor",
                role="doctor"
            )
            db.add(user_row)
            db.commit()
            db.refresh(user_row)
        else:
            if email and user_row.email != email:
                user_row.email = email
                db.commit()

        # Sync user profile to Firestore
        try:
            from app.db.firebase import save_user_profile, log_user_login
            save_user_profile(uid, email or user_row.email, name or user_row.display_name, user_row.role)
            log_user_login(uid, email or user_row.email, name or user_row.display_name, event="token_verified")
        except Exception:
            pass

        return UserInfo(
            uid=uid,
            email=email or user_row.email,
            display_name=name or user_row.display_name,
            role=user_row.role or "doctor"
        )

    except HTTPException:
        raise
    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase ID token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(
    user: UserInfo = Depends(verify_token)
) -> UserInfo:
    return user