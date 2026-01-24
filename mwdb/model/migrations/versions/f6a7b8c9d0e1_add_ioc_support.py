"""Add IOC (Indicator of Compromise) support

Revision ID: f6a7b8c9d0e1
Revises: 25ea40a798ac
Create Date: 2026-01-23 13:30:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f6a7b8c9d0e1"
down_revision = "25ea40a798ac"
branch_labels = None
depends_on = None


def upgrade():
    # Create a dedicated table for IOC subclass (joined-table inheritance)
    op.create_table(
        "ioc",
        sa.Column("id", sa.Integer(), sa.ForeignKey("object.id"), primary_key=True),
        sa.Column("ioc_type", sa.String(32), nullable=True, index=True),
        sa.Column("value", sa.String(1024, collation="C"), nullable=True, index=True),
        sa.Column("severity", sa.String(16), default="medium", nullable=True),
        sa.Column("source", sa.String(256), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=True, index=True),
    )

    # Create the ioc_object relationship table for many-to-many connections
    op.create_table(
        "ioc_object",
        sa.Column("ioc_id", sa.Integer(), nullable=False, index=True),
        sa.Column("object_id", sa.Integer(), nullable=False, index=True),
        sa.Column("creation_time", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ioc_id"], ["ioc.id"], ),
        sa.ForeignKeyConstraint(["object_id"], ["object.id"], ),
    )

    # Create the unique index on ioc_id and object_id
    op.create_index(
        "ix_ioc_object_ioc_object",
        "ioc_object",
        ["ioc_id", "object_id"],
        unique=True
    )

    # Add CHECK constraint for ioc_type to only allow valid IOC types (when set)
    op.execute("""
        ALTER TABLE ioc ADD CONSTRAINT ioc_type_valid CHECK (
            ioc_type IS NULL OR ioc_type IN (
                'ip', 'iprange', 'url', 'domain', 'email',
                'md5', 'sha1', 'sha256', 'sha512', 'ssdeep',
                'file_path', 'registry_key', 'c2_url', 'mutex', 'process_name'
            )
        );
    """)

    # Add CHECK constraint for severity to only allow valid severity levels (when set)
    op.execute("""
        ALTER TABLE ioc ADD CONSTRAINT severity_valid CHECK (
            severity IS NULL OR severity IN ('low', 'medium', 'high', 'critical')
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

    # Drop the ioc table
    op.drop_table("ioc")

