"""
RBAC Permission utilities and FastAPI dependencies.

Usage examples:

    # Require a specific permission
    @router.get("/users")
    async def list_users(
        current_user: User = Depends(require_permission("users:read"))
    ):
        ...

    # Require any of multiple permissions
    @router.get("/reports")
    async def view_reports(
        current_user: User = Depends(require_any_permission("reports:read", "admin:access"))
    ):
        ...

    # Require a specific role
    @router.post("/admin/settings")
    async def update_settings(
        current_user: User = Depends(require_role("admin"))
    ):
        ...

    # Check permission in code
    if has_permission(user, "vms:delete"):
        await delete_vm(vm_id)
"""

from typing import List, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status

from app.api.auth import get_current_user
from app.models.user import User


class PermissionDeniedError(HTTPException):
    """Raised when user doesn't have required permission"""
    def __init__(self, permission: str = None, role: str = None):
        if permission:
            detail = f"Permission denied: '{permission}' required"
        elif role:
            detail = f"Permission denied: role '{role}' required"
        else:
            detail = "Permission denied"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def require_permission(permission: str) -> Callable:
    """
    FastAPI dependency that requires a specific permission.

    Args:
        permission: Permission name in format 'resource:action' (e.g., 'users:read')

    Returns:
        Dependency function that returns the current user if permitted

    Raises:
        HTTPException 403 if user doesn't have the permission
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(permission):
            raise PermissionDeniedError(permission=permission)
        return current_user

    return permission_checker


def require_any_permission(*permissions: str) -> Callable:
    """
    FastAPI dependency that requires any one of the specified permissions.

    Args:
        *permissions: Variable permission names

    Returns:
        Dependency function that returns the current user if permitted
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_any_permission(*permissions):
            raise PermissionDeniedError(
                permission=" OR ".join(permissions)
            )
        return current_user

    return permission_checker


def require_all_permissions(*permissions: str) -> Callable:
    """
    FastAPI dependency that requires all of the specified permissions.

    Args:
        *permissions: Variable permission names

    Returns:
        Dependency function that returns the current user if permitted
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_all_permissions(*permissions):
            missing = [p for p in permissions if not current_user.has_permission(p)]
            raise PermissionDeniedError(
                permission=" AND ".join(missing)
            )
        return current_user

    return permission_checker


def require_role(role_name: str) -> Callable:
    """
    FastAPI dependency that requires a specific role.

    Args:
        role_name: Role name (e.g., 'admin', 'support')

    Returns:
        Dependency function that returns the current user if permitted
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_role(role_name):
            raise PermissionDeniedError(role=role_name)
        return current_user

    return role_checker


def require_any_role(*role_names: str) -> Callable:
    """
    FastAPI dependency that requires any one of the specified roles.

    Args:
        *role_names: Variable role names

    Returns:
        Dependency function that returns the current user if permitted
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not any(current_user.has_role(role) for role in role_names):
            raise PermissionDeniedError(
                role=" OR ".join(role_names)
            )
        return current_user

    return role_checker


# Convenience functions for checking permissions in code (not as dependencies)

def has_permission(user: User, permission: str) -> bool:
    """Check if user has a specific permission"""
    return user.has_permission(permission)


def has_role(user: User, role_name: str) -> bool:
    """Check if user has a specific role"""
    return user.has_role(role_name)


# Standard permission constants
class Permissions:
    """Standard permission names used across the application"""

    # Users
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_MANAGE = "users:manage"  # Full user management

    # VMs
    VMS_READ = "vms:read"
    VMS_CREATE = "vms:create"
    VMS_UPDATE = "vms:update"
    VMS_DELETE = "vms:delete"
    VMS_POWER = "vms:power"  # Start/stop/reboot
    VMS_CONSOLE = "vms:console"  # Access VM console
    VMS_MANAGE = "vms:manage"  # Full VM management

    # Volumes
    VOLUMES_READ = "volumes:read"
    VOLUMES_CREATE = "volumes:create"
    VOLUMES_UPDATE = "volumes:update"
    VOLUMES_DELETE = "volumes:delete"
    VOLUMES_MANAGE = "volumes:manage"

    # Networks
    NETWORKS_READ = "networks:read"
    NETWORKS_CREATE = "networks:create"
    NETWORKS_UPDATE = "networks:update"
    NETWORKS_DELETE = "networks:delete"
    NETWORKS_MANAGE = "networks:manage"

    # Security Groups
    SECURITY_GROUPS_READ = "security_groups:read"
    SECURITY_GROUPS_CREATE = "security_groups:create"
    SECURITY_GROUPS_UPDATE = "security_groups:update"
    SECURITY_GROUPS_DELETE = "security_groups:delete"
    SECURITY_GROUPS_MANAGE = "security_groups:manage"

    # Floating IPs
    FLOATING_IPS_READ = "floating_ips:read"
    FLOATING_IPS_CREATE = "floating_ips:create"
    FLOATING_IPS_UPDATE = "floating_ips:update"
    FLOATING_IPS_DELETE = "floating_ips:delete"
    FLOATING_IPS_MANAGE = "floating_ips:manage"

    # SSH Keys
    SSH_KEYS_READ = "ssh_keys:read"
    SSH_KEYS_CREATE = "ssh_keys:create"
    SSH_KEYS_DELETE = "ssh_keys:delete"
    SSH_KEYS_MANAGE = "ssh_keys:manage"

    # Snapshots
    SNAPSHOTS_READ = "snapshots:read"
    SNAPSHOTS_CREATE = "snapshots:create"
    SNAPSHOTS_DELETE = "snapshots:delete"
    SNAPSHOTS_MANAGE = "snapshots:manage"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_TOPUP = "billing:topup"
    BILLING_MANAGE = "billing:manage"  # Full billing access (admin)

    # Pricing (Admin)
    PRICING_READ = "pricing:read"
    PRICING_CREATE = "pricing:create"
    PRICING_UPDATE = "pricing:update"
    PRICING_DELETE = "pricing:delete"
    PRICING_MANAGE = "pricing:manage"

    # Admin
    ADMIN_ACCESS = "admin:access"  # Access admin panel
    ADMIN_USERS = "admin:users"  # Manage all users
    ADMIN_VMS = "admin:vms"  # Manage all VMs
    ADMIN_BILLING = "admin:billing"  # Manage billing/invoices
    ADMIN_PRICING = "admin:pricing"  # Manage pricing
    ADMIN_GROUPS = "admin:groups"  # Manage user groups
    ADMIN_RBAC = "admin:rbac"  # Manage roles and permissions
    ADMIN_SETTINGS = "admin:settings"  # System settings


class Roles:
    """Standard role names"""
    ADMIN = "admin"
    SUPPORT = "support"
    BILLING_MANAGER = "billing_manager"
    USER = "user"
