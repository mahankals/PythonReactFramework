"""Initial migration - Users, RBAC, Config

Revision ID: 001
Revises:
Create Date: 2025-12-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_superadmin', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Permissions table
    op.create_table('permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action')
    )
    op.create_index('ix_permissions_resource', 'permissions', ['resource'])

    # Roles table
    op.create_table('roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=True, default=False),
        sa.Column('priority', sa.Integer(), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Role-Permission association table
    op.create_table('role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # User-Role association table
    op.create_table('user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Password Reset Tokens table
    op.create_table('password_reset_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)

    # App Config table
    op.create_table('app_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('value_type', sa.String(20), nullable=True, default='string'),
        sa.Column('category', sa.String(50), nullable=True, default='general'),
        sa.Column('is_secret', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_editable', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_app_config_key', 'app_config', ['key'], unique=True)


def downgrade() -> None:
    op.drop_table('app_config')
    op.drop_table('password_reset_tokens')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('users')
