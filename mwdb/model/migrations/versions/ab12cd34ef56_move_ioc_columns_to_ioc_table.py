"""Move IOC columns from object table to dedicated ioc table (if present)

Revision ID: ab12cd34ef56
Revises: f6a7b8c9d0e1
Create Date: 2026-01-24 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "ab12cd34ef56"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def _column_exists(conn, table, column):
    row = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns WHERE table_name=:table AND column_name=:column"
        ),
        {"table": table, "column": column},
    ).fetchone()
    return row is not None


def _table_exists(conn, table):
    row = conn.execute(
        text("SELECT 1 FROM information_schema.tables WHERE table_name=:table"),
        {"table": table},
    ).fetchone()
    return row is not None


def upgrade():
    conn = op.get_bind()

    # If columns still exist on object table, migrate them to ioc table
    if _column_exists(conn, "object", "ioc_type"):
        # Ensure ioc table exists
        if not _table_exists(conn, "ioc"):
            op.create_table(
                "ioc",
                sa.Column("id", sa.Integer(), sa.ForeignKey("object.id"), primary_key=True),
                sa.Column("ioc_type", sa.String(32), nullable=True, index=True),
                sa.Column("value", sa.String(1024, collation="C"), nullable=True, index=True),
                sa.Column("severity", sa.String(16), default="medium", nullable=True),
                sa.Column("source", sa.String(256), nullable=True),
                sa.Column("is_active", sa.Boolean(), default=True, nullable=True, index=True),
            )
        # Copy values from object to ioc for rows that are IOC-type
        conn.execute(
            text(
                "INSERT INTO ioc (id, ioc_type, value, severity, source, is_active) "
                "SELECT id, ioc_type, value, severity, source, is_active FROM object WHERE type = 'ioc'"
            )
        )
        # Drop constraints on object if exist
        try:
            op.execute("ALTER TABLE object DROP CONSTRAINT IF EXISTS severity_valid;")
        except Exception:
            pass
        try:
            op.execute("ALTER TABLE object DROP CONSTRAINT IF EXISTS ioc_type_valid;")
        except Exception:
            pass
        # Drop columns from object
        for col in ("is_active", "source", "severity", "value", "ioc_type"):
            try:
                op.drop_column("object", col)
            except Exception:
                # If it was already dropped/doesn't exist - ignore
                pass


def downgrade():
    conn = op.get_bind()

    # If ioc table exists, move data back to object table columns
    if _table_exists(conn, "ioc") and not _column_exists(conn, "object", "ioc_type"):
        # Add columns back to object
        op.add_column("object", sa.Column("ioc_type", sa.String(32), nullable=True, index=True))
        op.add_column("object", sa.Column("value", sa.String(1024, collation="C"), nullable=True, index=True))
        op.add_column("object", sa.Column("severity", sa.String(16), default="medium", nullable=True))
        op.add_column("object", sa.Column("source", sa.String(256), nullable=True))
        op.add_column("object", sa.Column("is_active", sa.Boolean(), default=True, nullable=True, index=True))

        # Copy data back for IOC objects
        conn.execute(
            text(
                "UPDATE object SET (ioc_type, value, severity, source, is_active) = "
                "(SELECT ioc_type, value, severity, source, is_active FROM ioc WHERE ioc.id = object.id) "
                "WHERE type = 'ioc'"
            )
        )
        # Recreate constraints on object
        op.execute("""
            ALTER TABLE object ADD CONSTRAINT ioc_type_valid CHECK (
                ioc_type IS NULL OR ioc_type IN (
                    'ip', 'iprange', 'url', 'domain', 'email',
                    'md5', 'sha1', 'sha256', 'sha512', 'ssdeep',
                    'file_path', 'registry_key', 'c2_url', 'mutex', 'process_name'
                )
            );
        """)
        op.execute("""
            ALTER TABLE object ADD CONSTRAINT severity_valid CHECK (
                severity IS NULL OR severity IN ('low', 'medium', 'high', 'critical')
            );
        """)
    # Note: We do not drop the ioc table on downgrade to avoid data loss.
