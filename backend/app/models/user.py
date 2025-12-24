import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)

    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # RBAC - User can have multiple roles
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
        primaryjoin="User.id == user_roles.c.user_id",
        secondaryjoin="Role.id == user_roles.c.role_id"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        if self.is_superadmin:
            return True
        return any(role.name == role_name and role.is_active for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through any of their roles"""
        if self.is_superadmin:
            return True
        for role in self.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if permission.name == permission_name and permission.is_active:
                    return True
        return False

    def get_permissions(self) -> set:
        """Get all permission names this user has"""
        if self.is_superadmin:
            return {"*"}
        permissions = set()
        for role in self.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        permissions.add(permission.name)
        return permissions

    @property
    def is_admin(self) -> bool:
        """Check if user has admin access (superadmin or admin role)"""
        if self.is_superadmin:
            return True
        return any(role.name in ("admin", "superadmin") and role.is_active for role in self.roles)
