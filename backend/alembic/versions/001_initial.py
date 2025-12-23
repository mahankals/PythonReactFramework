"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-12-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
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
        sa.Column('account_type', sa.Enum('INDIVIDUAL', 'BUSINESS', name='accounttype'), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Regions table
    op.create_table('regions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('keystone_url', sa.String(255), nullable=False),
        sa.Column('nova_url', sa.String(255), nullable=False),
        sa.Column('glance_url', sa.String(255), nullable=False),
        sa.Column('cinder_url', sa.String(255), nullable=False),
        sa.Column('neutron_url', sa.String(255), nullable=False),
        sa.Column('admin_username', sa.String(100), nullable=False),
        sa.Column('admin_password', sa.String(255), nullable=False),
        sa.Column('admin_project', sa.String(100), nullable=False),
        sa.Column('admin_domain', sa.String(100), nullable=True, default='Default'),
        sa.Column('default_network_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('openstack_project_id', sa.String(100), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Flavors table
    op.create_table('flavors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('openstack_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('vcpus', sa.Integer(), nullable=False),
        sa.Column('ram_mb', sa.Integer(), nullable=False),
        sa.Column('disk_gb', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('price_hourly_inr', sa.Numeric(10, 4), nullable=True),
        sa.Column('price_monthly_inr', sa.Numeric(10, 2), nullable=True),
        sa.Column('price_hourly_usd', sa.Numeric(10, 4), nullable=True),
        sa.Column('price_monthly_usd', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'openstack_id', name='uq_flavor_region_openstack')
    )

    # Images table
    op.create_table('images',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('openstack_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('os_type', sa.String(50), nullable=True),
        sa.Column('os_distro', sa.String(50), nullable=True),
        sa.Column('os_version', sa.String(50), nullable=True),
        sa.Column('min_disk_gb', sa.Integer(), nullable=True, default=0),
        sa.Column('min_ram_mb', sa.Integer(), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('region_id', 'openstack_id', name='uq_image_region_openstack')
    )

    # Virtual Machines table
    op.create_table('virtual_machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('openstack_id', sa.String(100), nullable=True),
        sa.Column('flavor_id', sa.String(100), nullable=False),
        sa.Column('flavor_name', sa.String(100), nullable=True),
        sa.Column('vcpus', sa.Integer(), nullable=True),
        sa.Column('ram_mb', sa.Integer(), nullable=True),
        sa.Column('disk_gb', sa.Integer(), nullable=True),
        sa.Column('image_id', sa.String(100), nullable=False),
        sa.Column('image_name', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'BUILDING', 'ACTIVE', 'STOPPED', 'PAUSED', 'ERROR', 'DELETED', name='vmstatus'), nullable=False),
        sa.Column('power_state', sa.String(50), nullable=True),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('hourly_price', sa.Numeric(10, 4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Wallets table
    op.create_table('wallets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('balance', sa.Numeric(12, 2), nullable=True, default=0),
        sa.Column('currency', sa.String(3), nullable=True, default='INR'),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Wallet Transactions table
    op.create_table('wallet_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('wallet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('CREDIT', 'DEBIT', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('balance_after', sa.Numeric(12, 2), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('reference_type', sa.Enum('TOPUP', 'USAGE', 'REFUND', 'BONUS', name='referencetype'), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Usage Records table
    op.create_table('usage_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('hourly_rate', sa.Numeric(10, 4), nullable=False),
        sa.Column('total_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'BILLED', 'PAID', name='usagestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['vm_id'], ['virtual_machines.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('usage_records')
    op.drop_table('wallet_transactions')
    op.drop_table('wallets')
    op.drop_table('virtual_machines')
    op.drop_table('images')
    op.drop_table('flavors')
    op.drop_table('projects')
    op.drop_table('regions')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS usagestatus')
    op.execute('DROP TYPE IF EXISTS referencetype')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS vmstatus')
    op.execute('DROP TYPE IF EXISTS accounttype')
