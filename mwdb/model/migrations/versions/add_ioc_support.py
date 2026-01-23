"""Add IOC (Indicator of Compromise) support

This migration consolidates IOC table creation and configuration:
- Creates IOC table with all necessary columns
- Creates IOC-Object relationship table for linking IOCs to other objects
- Adds CHECK constraints for ioc_type and severity enum validation

Revision ID: 8f9a0b1c2d3e
Revises: e3241d250d0c
Create Date: 2026-01-23 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f9a0b1c2d3e"
down_revision = "e3241d250d0c"
branch_labels = None
depends_on = None


def upgrade():
    # Create IOC table with inherited columns from object table
    op.create_table(
        "ioc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ioc_type", sa.String(32), nullable=False, index=True),
        sa.Column("value", sa.String(1024), nullable=False, index=True),
        sa.Column("severity", sa.String(16), default="medium", nullable=False),
        sa.Column("source", sa.String(256), nullable=True),
        sa.Column("last_seen", sa.DateTime(), nullable=True, index=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False, index=True),
        sa.ForeignKeyConstraint(["id"], ["object.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indices for common IOC queries
    op.create_index("ix_ioc_type_value", "ioc", ["ioc_type", "value"])
    op.create_index("ix_ioc_severity", "ioc", ["severity"])
    
    # Create the ioc_object relationship table
    op.create_table(
        "ioc_object",
        sa.Column("ioc_id", sa.Integer(), nullable=False, index=True),
        sa.Column("object_id", sa.Integer(), nullable=False, index=True),
        sa.Column("creation_time", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ioc_id"], ["object.id"], ),
        sa.ForeignKeyConstraint(["object_id"], ["object.id"], ),
    )
    
    # Create the unique index on ioc_id and object_id
    op.create_index(
        "ix_ioc_object_ioc_object",
        "ioc_object",
        ["ioc_id", "object_id"],
        unique=True
    )
    
    # Add CHECK constraint for ioc_type to only allow valid IOC types
    op.execute("""
        ALTER TABLE ioc ADD CONSTRAINT ioc_type_valid CHECK (
            ioc_type IN (
                'ip', 'iprange', 'url', 'domain', 'email',
                'md5', 'sha1', 'sha256', 'sha512', 'ssdeep',
                'file_path', 'registry_key', 'c2_url', 'mutex', 'process_name'
            )
        );
    """)
    
    # Add CHECK constraint for severity to only allow valid severity levels
    op.execute("""
        ALTER TABLE ioc ADD CONSTRAINT severity_valid CHECK (
            severity IN ('low', 'medium', 'high', 'critical')
        );
    """)


def downgrade():
    # Drop constraints
    op.execute("ALTER TABLE ioc DROP CONSTRAINT severity_valid;")
    op.execute("ALTER TABLE ioc DROP CONSTRAINT ioc_type_valid;")
    
    # Drop the index
    op.drop_index("ix_ioc_object_ioc_object", table_name="ioc_object")
    
    # Drop the ioc_object table
    op.drop_table("ioc_object")
    
    # Drop indices
    op.drop_index("ix_ioc_severity", table_name="ioc")
    op.drop_index("ix_ioc_type_value", table_name="ioc")
    
    # Drop IOC table
    op.drop_table("ioc")
