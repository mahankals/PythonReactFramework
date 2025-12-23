"""RBAC (Role-Based Access Control) models for granular permission management"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Table, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# Association table for Role-Permission many-to-many
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
)

# Association table for User-Role many-to-many
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', UUID(as_uuid=True), ForeignKey('users.id'), nullable=True),
)


class Permission(Base):
    """
    Granular permissions for specific actions on resources.
    Format: resource:action (e.g., 'users:read', 'vms:create', 'billing:manage')
    """
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)  # e.g., 'users:read'
    display_name = Column(String(150), nullable=False)  # e.g., 'View Users'
    description = Column(Text, nullable=True)

    # Categorization
    resource = Column(String(50), nullable=False)  # e.g., 'users', 'vms', 'billing'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'create', 'update', 'delete', 'manage'

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )


class Role(Base):
    """
    Roles group permissions together for easier management.
    Users can have multiple roles, and roles can have multiple permissions.
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)  # e.g., 'admin', 'support', 'billing_manager'
    display_name = Column(String(100), nullable=False)  # e.g., 'Administrator', 'Support Staff'
    description = Column(Text, nullable=True)

    # System roles cannot be deleted or modified
    is_system = Column(Boolean, default=False)

    # Priority for permission resolution (higher = more important)
    priority = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        foreign_keys=[user_roles.c.role_id, user_roles.c.user_id]
    )
