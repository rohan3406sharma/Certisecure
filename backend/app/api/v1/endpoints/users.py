from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse, ResponseBase
from app.schemas.user import UserRead, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams, pagination_params

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserRead], dependencies=[Depends(require_admin)])
async def list_users(pg: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    users, total = await svc.get_all(page=pg.page, page_size=pg.page_size)
    return PaginatedResponse(
        total=total, page=pg.page, page_size=pg.page_size,
        total_pages=UserService.total_pages(total, pg.page_size),
        items=[UserRead.model_validate(u) for u in users],
    )


@router.get("/me", response_model=ResponseBase[UserRead])
async def get_me(current_user: User = Depends(get_current_user)):
    return ResponseBase(data=UserRead.model_validate(current_user))


@router.patch("/me", response_model=ResponseBase[UserRead])
async def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.role and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change roles.")
    updated = await UserService(db).update(current_user, payload)
    return ResponseBase(message="Profile updated.", data=UserRead.model_validate(updated))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await UserService(db).delete(current_user)


@router.get("/{user_id}", response_model=ResponseBase[UserRead], dependencies=[Depends(require_admin)])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return ResponseBase(data=UserRead.model_validate(user))


@router.patch("/{user_id}", response_model=ResponseBase[UserRead], dependencies=[Depends(require_admin)])
async def admin_update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    svc = UserService(db)
    user = await svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    updated = await svc.update(user, payload)
    return ResponseBase(message="User updated.", data=UserRead.model_validate(updated))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def admin_delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await UserService(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await UserService(db).delete(user)
