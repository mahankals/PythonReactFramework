"""
Startup initialization: auto-seeds RBAC permissions, roles, and superadmin.
Called automatically on first application startup.
"""
import logging
from passlib.context import CryptContext
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.rbac import Role, Permission
from app.models.config import AppConfig, DEFAULT_CONFIG
from app.config import settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def check_migrations_applied(db: AsyncSession) -> bool:
    """Check if database migrations have been applied."""
    try:
        result = await db.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
        )
        return result.scalar()
    except Exception:
        return False


# Default permissions for SampleApp
DEFAULT_PERMISSIONS = [
    # Users
    {"name": "users:read", "display_name": "View Users", "resource": "users", "action": "read"},
    {"name": "users:create", "display_name": "Create Users", "resource": "users", "action": "create"},
    {"name": "users:update", "display_name": "Update Users", "resource": "users", "action": "update"},
    {"name": "users:delete", "display_name": "Delete Users", "resource": "users", "action": "delete"},

    # Roles
    {"name": "roles:read", "display_name": "View Roles", "resource": "roles", "action": "read"},
    {"name": "roles:create", "display_name": "Create Roles", "resource": "roles", "action": "create"},
    {"name": "roles:update", "display_name": "Update Roles", "resource": "roles", "action": "update"},
    {"name": "roles:delete", "display_name": "Delete Roles", "resource": "roles", "action": "delete"},

    # Settings
    {"name": "settings:read", "display_name": "View Settings", "resource": "settings", "action": "read"},
    {"name": "settings:update", "display_name": "Update Settings", "resource": "settings", "action": "update"},

    # Admin
    {"name": "admin:access", "display_name": "Admin Panel Access", "resource": "admin", "action": "access"},
]

# Default roles
DEFAULT_ROLES = [
    {
        "name": "superadmin",
        "display_name": "Super Admin",
        "description": "Full system control - assigned via create_admin command only",
        "is_system": True,
        "priority": 100,
        "permissions": "*",  # All permissions
    },
    {
        "name": "admin",
        "display_name": "Administrator",
        "description": "Administrative access",
        "is_system": True,
        "permissions": [
            "users:read", "users:create", "users:update", "users:delete",
            "roles:read", "roles:create", "roles:update", "roles:delete",
            "settings:read", "settings:update",
            "admin:access",
        ]
    },
    {
        "name": "user",
        "display_name": "Standard User",
        "description": "Regular user with basic access",
        "is_system": True,
        "permissions": []
    },
]


async def seed_permissions(db: AsyncSession) -> dict:
    """Seed default permissions, returns map of name -> Permission."""
    permission_map = {}

    for perm_data in DEFAULT_PERMISSIONS:
        result = await db.execute(
            select(Permission).where(Permission.name == perm_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            permission_map[perm_data["name"]] = existing
        else:
            permission = Permission(
                name=perm_data["name"],
                display_name=perm_data["display_name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                is_active=True,
            )
            db.add(permission)
            await db.flush()
            permission_map[perm_data["name"]] = permission
            logger.info(f"Created permission: {perm_data['name']}")

    return permission_map


async def seed_roles(db: AsyncSession, permission_map: dict):
    """Seed default roles with permissions."""
    for role_data in DEFAULT_ROLES:
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == role_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update permissions for existing role
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

            # Reload with permissions
            result = await db.execute(
                select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role.id)
            )
            role = result.scalar_one()
            logger.info(f"Created role: {role_data['name']}")

        # Assign permissions ("*" means all permissions)
        perms = role_data.get("permissions", [])
        if perms == "*":
            role.permissions = list(permission_map.values())
        else:
            role_perms = []
            for perm_name in perms:
                if perm_name in permission_map:
                    role_perms.append(permission_map[perm_name])
            role.permissions = role_perms


async def seed_superadmin(db: AsyncSession):
    """Create superadmin from environment settings if not exists."""
    result = await db.execute(
        select(User).where(User.email == settings.superadmin_email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.debug(f"Superadmin {settings.superadmin_email} already exists")
        return

    # Get superadmin role
    result = await db.execute(select(Role).where(Role.name == "superadmin"))
    superadmin_role = result.scalar_one_or_none()

    user = User(
        email=settings.superadmin_email,
        password_hash=pwd_context.hash(settings.superadmin_password),
        first_name=settings.superadmin_first_name,
        last_name=settings.superadmin_last_name,
        is_superadmin=True,
        is_active=True,
        email_verified=True,
        roles=[superadmin_role] if superadmin_role else [],
    )
    db.add(user)
    logger.info(f"Created superadmin: {settings.superadmin_email}")


async def seed_config(db: AsyncSession):
    """Seed default configuration values."""
    added = 0
    for config_data in DEFAULT_CONFIG:
        result = await db.execute(
            select(AppConfig).where(AppConfig.key == config_data["key"])
        )
        if not result.scalar_one_or_none():
            config = AppConfig(**config_data)
            db.add(config)
            added += 1

    if added > 0:
        logger.info(f"Seeded {added} default configuration items")


async def run_startup_tasks(db: AsyncSession):
    """Run all startup initialization tasks."""
    logger.info("Running startup initialization...")

    # Check if migrations have been applied
    if not await check_migrations_applied(db):
        logger.warning(
            "Database tables not found. Run migrations first: "
            "docker compose exec backend alembic upgrade head"
        )
        return

    # Seed RBAC
    permission_map = await seed_permissions(db)
    await seed_roles(db, permission_map)

    # Seed superadmin
    await seed_superadmin(db)

    # Seed config
    await seed_config(db)

    await db.commit()
    logger.info("Startup initialization complete")
