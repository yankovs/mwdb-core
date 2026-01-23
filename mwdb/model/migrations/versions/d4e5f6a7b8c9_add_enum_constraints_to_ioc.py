"""Add enum constraints to IOC table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-23 12:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
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
