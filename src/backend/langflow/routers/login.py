from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from langflow.services.utils import get_session
from langflow.database.models.token import Token
from langflow.auth.auth import (
    authenticate_user,
    create_user_tokens,
    create_refresh_token,
    create_user_longterm_token,
)

from langflow.services.utils import get_settings_manager

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_to_get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
    # _: Session = Depends(get_current_active_user)
):
    if user := authenticate_user(form_data.username, form_data.password, db):
        return create_user_tokens(user_id=user.id, db=db, update_last_login=True)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/auto_login")
async def auto_login(db: Session = Depends(get_session)):
    settings_manager = get_settings_manager()

    if settings_manager.settings.AUTO_LOGIN:
        user_id = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        return create_user_longterm_token(user_id, db)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Auto login is disabled. Please enable it in the settings",
            "auto_login": False,
        },
    )


@router.post("/refresh")
async def refresh_token(token: str):
    if token:
        return create_refresh_token(token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
