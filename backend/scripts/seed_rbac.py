#!/usr/bin/env python3
"""
Seed RBAC (Role-Based Access Control) data for CloudPe CMP

Usage:
    docker-compose exec backend python scripts/seed_rbac.py

This script creates:
- Default permissions for all resources
- Default roles (admin, support, billing_manager, user)
- Maps permissions to roles
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.rbac import Role, Permission


# Default permissions by resource
DEFAULT_PERMISSIONS = [
    # Users
    {"name": "users:read", "display_name": "View Users", "resource": "users", "action": "read", "description": "View user list and details"},
    {"name": "users:create", "display_name": "Create Users", "resource": "users", "action": "create", "description": "Create new users"},
    {"name": "users:update", "display_name": "Update Users", "resource": "users", "action": "update", "description": "Update user information"},
    {"name": "users:delete", "display_name": "Delete Users", "resource": "users", "action": "delete", "description": "Delete users"},
    {"name": "users:manage", "display_name": "Manage Users", "resource": "users", "action": "manage", "description": "Full user management access"},

    # Admin
    {"name": "admin:access", "display_name": "Admin Panel Access", "resource": "admin", "action": "access", "description": "Access admin panel"},
    {"name": "admin:users", "display_name": "Admin User Management", "resource": "admin", "action": "users", "description": "Manage all users (admin view)"},
    {"name": "admin:vms", "display_name": "Admin VM Management", "resource": "admin", "action": "vms", "description": "Manage all VMs (admin view)"},
    {"name": "admin:billing", "display_name": "Admin Billing Management", "resource": "admin", "action": "billing", "description": "Manage billing and invoices"},
    {"name": "admin:pricing", "display_name": "Admin Pricing Management", "resource": "admin", "action": "pricing", "description": "Manage pricing configuration"},
    {"name": "admin:groups", "display_name": "Admin Group Management", "resource": "admin", "action": "groups", "description": "Manage user groups"},
    {"name": "admin:rbac", "display_name": "Admin RBAC Management", "resource": "admin", "action": "rbac", "description": "Manage roles and permissions"},
    {"name": "admin:settings", "display_name": "Admin Settings", "resource": "admin", "action": "settings", "description": "Manage system settings"},
]

# Default roles with their permissions
DEFAULT_ROLES = [
    {
        "name": "admin",
        "display_name": "Administrator",
        "description": "Full administrative access to all system features",
        "is_system": True,
        "priority": 100,
        "permissions": [
            # All admin permissions
            "admin:access", "admin:users", "admin:vms", "admin:billing",
            "admin:pricing", "admin:groups", "admin:rbac", "admin:settings",
            # All resource management
            "users:manage", "vms:manage", "volumes:manage", "networks:manage",
            "security_groups:manage", "floating_ips:manage", "ssh_keys:manage",
            "snapshots:manage", "billing:manage", "pricing:manage",
        ]
    },
    {
        "name": "user",
        "display_name": "Standard User",
        "description": "Regular user with access to their own resources",
        "is_system": True,
        "priority": 10,
        "permissions": [
            # VMs
            "vms:read", "vms:create", "vms:update", "vms:delete", "vms:power", "vms:console",
            # Volumes
            "volumes:read", "volumes:create", "volumes:update", "volumes:delete",
            # Networks
            "networks:read", "networks:create", "networks:update", "networks:delete",
            # Security Groups
            "security_groups:read", "security_groups:create", "security_groups:update", "security_groups:delete",
            # Floating IPs
            "floating_ips:read", "floating_ips:create", "floating_ips:update", "floating_ips:delete",
            # SSH Keys
            "ssh_keys:read", "ssh_keys:create", "ssh_keys:delete",
            # Snapshots
            "snapshots:read", "snapshots:create", "snapshots:delete",
            # Billing (own)
            "billing:read", "billing:topup",
        ]
    },
]


async def seed_rbac():
    """Seed RBAC data"""

    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        # Create permissions
        print("Creating permissions...")
        permission_map = {}

        for perm_data in DEFAULT_PERMISSIONS:
            # Check if permission already exists
            result = await db.execute(
                select(Permission).where(Permission.name == perm_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Permission '{perm_data['name']}' already exists, skipping")
                permission_map[perm_data["name"]] = existing
            else:
                permission = Permission(
                    name=perm_data["name"],
                    display_name=perm_data["display_name"],
                    description=perm_data.get("description"),
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    is_active=True,
                )
                db.add(permission)
                await db.flush()
                permission_map[perm_data["name"]] = permission
                print(f"  Created permission: {perm_data['name']}")

        print(f"\nTotal permissions: {len(permission_map)}")

        # Create roles with permissions
        print("\nCreating roles...")

        from sqlalchemy.orm import selectinload

        for role_data in DEFAULT_ROLES:
            # Check if role already exists
            result = await db.execute(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.name == role_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Role '{role_data['name']}' already exists, updating permissions...")
                role = existing
            else:
                role = Role(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data.get("description"),
                    is_system=role_data.get("is_system", False),
                    priority=role_data.get("priority", 0),
                    is_active=True,
                )
                db.add(role)
                await db.flush()

                # Reload with permissions relationship
                result = await db.execute(
                    select(Role)
                    .options(selectinload(Role.permissions))
                    .where(Role.id == role.id)
                )
                role = result.scalar_one()
                print(f"  Created role: {role_data['name']}")

            # Assign permissions to role
            role_perms = []
            for perm_name in role_data.get("permissions", []):
                if perm_name in permission_map:
                    role_perms.append(permission_map[perm_name])
                else:
                    print(f"    Warning: Permission '{perm_name}' not found")

            role.permissions = role_perms
            print(f"    Assigned {len(role_perms)} permissions to {role_data['name']}")

        await db.commit()
        print("\nRBAC data seeded successfully!")

        # Summary
        print("\n" + "=" * 50)
        print("RBAC Summary:")
        print("=" * 50)

        result = await db.execute(select(Role))
        roles = result.scalars().all()
        for role in roles:
            print(f"\n{role.display_name} ({role.name}):")
            print(f"  System role: {role.is_system}")
            print(f"  Priority: {role.priority}")
            print(f"  Permissions: {len(role.permissions)}")

    await engine.dispose()


if __name__ == "__main__":
    print("Seeding RBAC data for CloudPe CMP...\n")
    asyncio.run(seed_rbac())
