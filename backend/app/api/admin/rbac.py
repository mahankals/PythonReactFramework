"""Admin API for managing roles, permissions, and user role assignments"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.auth import get_current_admin_user
from app.models.user import User
from app.models.rbac import Role, Permission, role_permissions, user_roles
from app.utils.permissions import require_permission, Permissions

router = APIRouter()


# ============= Pydantic Schemas =============

class PermissionCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    resource: str
    action: str
    is_active: bool = True


class PermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str]
    resource: str
    action: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    priority: int = 0
    is_active: bool = True
    permission_ids: Optional[List[str]] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str]
    is_system: bool
    priority: int
    is_active: bool
    permissions: List[PermissionResponse] = []
    user_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    permission_ids: List[str]


class UserRoleAssignment(BaseModel):
    role_ids: List[str]


class UserRoleResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    roles: List[RoleResponse]

    class Config:
        from_attributes = True


# ============= Helper Functions =============

def permission_to_response(permission: Permission) -> PermissionResponse:
    return PermissionResponse(
        id=str(permission.id),
        name=permission.name,
        display_name=permission.display_name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action,
        is_active=permission.is_active,
        created_at=permission.created_at,
    )


def role_to_response(role: Role, user_count: int = 0) -> RoleResponse:
    return RoleResponse(
        id=str(role.id),
        name=role.name,
        display_name=role.display_name,
        description=role.description,
        is_system=role.is_system,
        priority=role.priority,
        is_active=role.is_active,
        permissions=[permission_to_response(p) for p in role.permissions] if role.permissions else [],
        user_count=user_count,
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


# ============= Permission Endpoints =============

@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    resource: Optional[str] = Query(None, description="Filter by resource"),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all permissions with optional filters"""
    query = select(Permission)

    if resource:
        query = query.where(Permission.resource == resource)
    if is_active is not None:
        query = query.where(Permission.is_active == is_active)

    query = query.order_by(Permission.resource, Permission.action)

    result = await db.execute(query)
    permissions = result.scalars().all()

    return [permission_to_response(p) for p in permissions]


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    data: PermissionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new permission"""
    # Check for duplicate name
    result = await db.execute(
        select(Permission).where(Permission.name == data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Permission with this name already exists")

    # Check for duplicate resource:action
    result = await db.execute(
        select(Permission).where(
            Permission.resource == data.resource,
            Permission.action == data.action
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Permission {data.resource}:{data.action} already exists")

    permission = Permission(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        resource=data.resource,
        action=data.action,
        is_active=data.is_active,
    )

    db.add(permission)
    await db.commit()
    await db.refresh(permission)

    return permission_to_response(permission)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific permission"""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    return permission_to_response(permission)


@router.patch("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: UUID,
    data: PermissionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a permission (cannot change name, resource, or action)"""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if data.display_name is not None:
        permission.display_name = data.display_name
    if data.description is not None:
        permission.description = data.description
    if data.is_active is not None:
        permission.is_active = data.is_active

    await db.commit()
    await db.refresh(permission)

    return permission_to_response(permission)


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a permission"""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    await db.delete(permission)
    await db.commit()

    return {"message": "Permission deleted successfully"}


# ============= Role Endpoints =============

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all roles with their permissions"""
    query = (
        select(Role)
        .options(selectinload(Role.permissions))
    )

    if is_active is not None:
        query = query.where(Role.is_active == is_active)

    query = query.order_by(Role.priority.desc(), Role.name)

    result = await db.execute(query)
    roles = result.scalars().all()

    # Get user counts for each role
    role_user_counts = {}
    for role in roles:
        count_query = select(func.count()).select_from(user_roles).where(
            user_roles.c.role_id == role.id
        )
        count_result = await db.execute(count_query)
        role_user_counts[role.id] = count_result.scalar() or 0

    return [role_to_response(r, role_user_counts.get(r.id, 0)) for r in roles]


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    data: RoleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new role with optional permissions"""
    # Check for duplicate name
    result = await db.execute(
        select(Role).where(Role.name == data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role with this name already exists")

    role = Role(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        priority=data.priority,
        is_active=data.is_active,
        is_system=False,
    )

    # Add permissions if provided
    if data.permission_ids:
        result = await db.execute(
            select(Permission).where(Permission.id.in_([UUID(pid) for pid in data.permission_ids]))
        )
        permissions = result.scalars().all()
        role.permissions = list(permissions)

    db.add(role)
    await db.commit()
    await db.refresh(role)

    # Reload with permissions
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role.id)
    )
    role = result.scalar_one()

    return role_to_response(role)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific role with its permissions"""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Get user count
    count_query = select(func.count()).select_from(user_roles).where(
        user_roles.c.role_id == role.id
    )
    count_result = await db.execute(count_query)
    user_count = count_result.scalar() or 0

    return role_to_response(role, user_count)


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a role (cannot modify system roles except is_active)"""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # System roles can only have is_active changed
    if role.is_system:
        if data.is_active is not None:
            role.is_active = data.is_active
        else:
            raise HTTPException(status_code=400, detail="Cannot modify system role properties")
    else:
        if data.name is not None:
            # Check for duplicate name
            result = await db.execute(
                select(Role).where(Role.name == data.name, Role.id != role_id)
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Role with this name already exists")
            role.name = data.name

        if data.display_name is not None:
            role.display_name = data.display_name
        if data.description is not None:
            role.description = data.description
        if data.priority is not None:
            role.priority = data.priority
        if data.is_active is not None:
            role.is_active = data.is_active

    await db.commit()
    await db.refresh(role)

    return role_to_response(role)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a role (cannot delete system roles)"""
    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system role")

    await db.delete(role)
    await db.commit()

    return {"message": "Role deleted successfully"}


# ============= Role Permission Management =============

@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
async def set_role_permissions(
    role_id: UUID,
    data: RolePermissionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Set all permissions for a role (replaces existing)"""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify permissions of system role")

    # Get requested permissions
    result = await db.execute(
        select(Permission).where(Permission.id.in_([UUID(pid) for pid in data.permission_ids]))
    )
    permissions = result.scalars().all()

    # Replace permissions
    role.permissions = list(permissions)

    await db.commit()
    await db.refresh(role)

    return role_to_response(role)


@router.post("/roles/{role_id}/permissions/{permission_id}")
async def add_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a single permission to a role"""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify permissions of system role")

    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission not in role.permissions:
        role.permissions.append(permission)
        await db.commit()

    return {"message": f"Permission '{permission.name}' added to role '{role.name}'"}


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a permission from a role"""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify permissions of system role")

    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission in role.permissions:
        role.permissions.remove(permission)
        await db.commit()

    return {"message": f"Permission '{permission.name}' removed from role '{role.name}'"}


# ============= User Role Management =============

@router.get("/users/{user_id}/roles", response_model=UserRoleResponse)
async def get_user_roles(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all roles assigned to a user"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRoleResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=[role_to_response(r) for r in user.roles]
    )


@router.put("/users/{user_id}/roles", response_model=UserRoleResponse)
async def set_user_roles(
    user_id: UUID,
    data: UserRoleAssignment,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Set all roles for a user (replaces existing)"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get requested roles
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id.in_([UUID(rid) for rid in data.role_ids]))
    )
    roles = result.scalars().all()

    # Replace roles
    user.roles = list(roles)

    await db.commit()
    await db.refresh(user)

    return UserRoleResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=[role_to_response(r) for r in user.roles]
    )


@router.post("/users/{user_id}/roles/{role_id}")
async def add_role_to_user(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a single role to a user"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        user.roles.append(role)
        await db.commit()

    return {"message": f"Role '{role.display_name}' assigned to user '{user.email}'"}


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a role from a user"""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        user.roles.remove(role)
        await db.commit()

    return {"message": f"Role '{role.display_name}' removed from user '{user.email}'"}


# ============= Utility Endpoints =============

@router.get("/resources")
async def list_resources(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of all unique resources from permissions"""
    result = await db.execute(
        select(Permission.resource).distinct().order_by(Permission.resource)
    )
    resources = [row[0] for row in result.all()]
    return {"resources": resources}


@router.get("/actions")
async def list_actions(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of all unique actions from permissions"""
    result = await db.execute(
        select(Permission.action).distinct().order_by(Permission.action)
    )
    actions = [row[0] for row in result.all()]
    return {"actions": actions}
