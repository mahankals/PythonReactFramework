import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import enum

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


    # Billing details (for invoicing)
    billing_address = Column(String(500), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_pincode = Column(String(10), nullable=True)
    billing_country = Column(String(100), default="India")
    gstin = Column(String(20), nullable=True)  # GST Identification Number

    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)

    # Phone verification
    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime, nullable=True)

    # KYC verification
    kyc_status = Column(String(20), default='PENDING')  # PENDING, IN_PROGRESS, VERIFIED, FAILED
    kyc_verified_at = Column(DateTime, nullable=True)
    kyc_data = Column(JSON, nullable=True)  # Stores KYC response data from Digio
    digio_request_id = Column(String(100), nullable=True)

    # Signup tracking
    use_case = Column(String(50), nullable=True)  # PERSONAL, STARTUP, ENTERPRISE, AGENCY, OTHER
    signup_step = Column(Integer, default=5)  # Track signup progress: 1-5
    signup_completed = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
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
        if self.is_admin:  # Super admin has all roles
            return True
        return any(role.name == role_name and role.is_active for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission through any of their roles"""
        if self.is_admin:  # Super admin has all permissions
            return True
        for role in self.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if permission.name == permission_name and permission.is_active:
                    return True
        return False

    def has_any_permission(self, *permission_names: str) -> bool:
        """Check if user has any of the specified permissions"""
        if self.is_admin:
            return True
        return any(self.has_permission(perm) for perm in permission_names)

    def has_all_permissions(self, *permission_names: str) -> bool:
        """Check if user has all of the specified permissions"""
        if self.is_admin:
            return True
        return all(self.has_permission(perm) for perm in permission_names)

    def get_permissions(self) -> set:
        """Get all permission names this user has"""
        if self.is_admin:
            return {"*"}  # Super admin has all permissions
        permissions = set()
        for role in self.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        permissions.add(permission.name)
        return permissions

    def get_role_names(self) -> list:
        """Get list of active role names for this user"""
        if self.is_admin:
            return ["admin"]
        return [role.name for role in self.roles if role.is_active]
