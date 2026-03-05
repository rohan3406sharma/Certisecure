from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.schemas.common import ResponseBase
from app.schemas.token import RefreshRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=ResponseBase[UserRead], status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    if await svc.get_by_email(payload.email):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    user = await svc.create(payload)
    return ResponseBase(message="Account created successfully.", data=UserRead.model_validate(user))


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    user = await svc.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="This account has been deactivated.")
    return Token(
        access_token=create_access_token(user.id, role=user.role),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
    user_id = payload.get("sub")
    user = await UserService(db).get_by_id(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User no longer exists or is inactive.")
    return Token(
        access_token=create_access_token(user.id, role=user.role),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=ResponseBase[UserRead])
async def me(current_user=Depends(get_current_user)):
    return ResponseBase(data=UserRead.model_validate(current_user))
