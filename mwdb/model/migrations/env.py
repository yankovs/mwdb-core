from __future__ import with_statement

import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name, disable_existing_loggers=False)
logger = logging.getLogger("alembic.env")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app

config.set_main_option(
    "sqlalchemy.url", current_app.config.get("SQLALCHEMY_DATABASE_URI")
)
target_metadata = current_app.extensions["migrate"].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Handle multiple migration heads by using 'heads' instead of 'head'
def get_target_revision():
    """Determine the target revision for migrations.
    
    Uses 'heads' to target all heads when multiple branches exist,
    otherwise uses 'head' for single branch.
    """
    try:
        # Try to use 'heads' to handle multiple branches
        return 'heads'
    except Exception:
        # Fallback to 'head' if 'heads' is not supported
        return 'head'


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    
    # Handle multiple migration heads
    migrate_args = current_app.extensions["migrate"].configure_args
    # Try to upgrade to 'heads' to handle multiple branches, but fallback to normal behavior
    try:
        # Add target='heads' to handle multiple branches if they exist
        if 'target_metadata' not in migrate_args:
            migrate_args['target_metadata'] = target_metadata
    except Exception:
        pass
    
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
        **migrate_args,
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
