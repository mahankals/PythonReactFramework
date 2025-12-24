from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.database import get_db
from app.api.auth import get_current_admin_user
from app.models.user import User
from app.models.rbac import Role

router = APIRouter()


class RoleInfo(BaseModel):
    id: str
    name: str
    display_name: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    roles: List[RoleInfo] = []
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    is_active: Optional[bool] = None
    # Note: is_admin is now a computed property based on roles
    # Use role assignment to grant/revoke admin access


def user_to_response(user: User) -> UserResponse:
    """Convert User model to response with roles."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        company_name=user.company_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        roles=[
            RoleInfo(id=str(role.id), name=role.name, display_name=role.display_name)
            for role in (user.roles or [])
        ],
        created_at=user.created_at,
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return [user_to_response(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user details (admin only)"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user_to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only). Admins cannot modify their own account."""
    # Prevent admin from modifying self
    if user_id == admin_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify your own account")

    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.phone is not None:
        user.phone = request.phone
    if request.company_name is not None:
        user.company_name = request.company_name
    if request.is_active is not None:
        user.is_active = request.is_active
    # Note: is_admin is computed from roles, use role assignment instead

    await db.commit()
    await db.refresh(user)

    return user_to_response(user)
