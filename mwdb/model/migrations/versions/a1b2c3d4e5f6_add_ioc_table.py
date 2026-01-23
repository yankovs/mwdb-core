"""Add IOC (Indicator of Compromise) table

Revision ID: a1b2c3d4e5f6
Revises: e3241d250d0c
Create Date: 2026-01-23 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
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


def downgrade():
    # Drop indices
    op.drop_index("ix_ioc_severity", table_name="ioc")
    op.drop_index("ix_ioc_type_value", table_name="ioc")
    
    # Drop IOC table
    op.drop_table("ioc")
