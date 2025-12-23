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


class UserListResponse(BaseModel):
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
    is_admin: Optional[bool] = None


@router.get("", response_model=List[UserListResponse])
async def list_users(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    response = []
    for user in users:
        # VM and Billing features removed — return defaults
        vm_count = 0
        balance = 0.0
        
        response.append(UserListResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            account_type=getattr(user, 'account_type', None),
            is_active=user.is_active,
            is_admin=user.is_admin,
            vm_count=vm_count,
            wallet_balance=balance,
            created_at=user.created_at,
        ))
    
    return response


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user details (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # VM and Billing features removed — return defaults
    vm_count = 0
    balance = 0.0
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        company_name=user.company_name,
        account_type=user.account_type,
        is_active=user.is_active,
        is_admin=user.is_admin,
        vm_count=vm_count,
        wallet_balance=balance,
        created_at=user.created_at,
    )


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_admin is not None:
        user.is_admin = request.is_admin
    
    await db.commit()
    await db.refresh(user)
    
    # Get counts for response
    # VM and Billing features removed — return defaults
    vm_count = 0
    balance = 0.0
    
    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        company_name=user.company_name,
        account_type=user.account_type,
        is_active=user.is_active,
        is_admin=user.is_admin,
        vm_count=vm_count,
        wallet_balance=balance,
        created_at=user.created_at,
    )
