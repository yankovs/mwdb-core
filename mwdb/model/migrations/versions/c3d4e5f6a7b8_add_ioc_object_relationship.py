"""Add IOC-Object relationship table

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
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


def downgrade():
    # Drop the index
    op.drop_index("ix_ioc_object_ioc_object", table_name="ioc_object")
    
    # Drop the table
    op.drop_table("ioc_object")
