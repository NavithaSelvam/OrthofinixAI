from fastapi import APIRouter, Depends
from app.models.schemas import UserInfo
from app.api.dependencies import get_current_user
from app.db.firebase import save_user_profile, log_user_login

router = APIRouter(prefix="/auth")

@router.get("/me", response_model=UserInfo)
def get_me(current_user: UserInfo = Depends(get_current_user)):
    """
    Get the currently authenticated Firebase user profile based on Bearer token.
    """
    return current_user

@router.post("/sync", response_model=UserInfo)
def sync_user(current_user: UserInfo = Depends(get_current_user)):
    """
    Explicitly syncs user profile and logs a login event into Firestore root collections.
    """
    save_user_profile(
        user_id=current_user.uid,
        email=current_user.email,
        display_name=current_user.display_name,
        role=current_user.role
    )
    log_user_login(
        user_id=current_user.uid,
        email=current_user.email,
        display_name=current_user.display_name,
        event="login"
    )
    return current_user

