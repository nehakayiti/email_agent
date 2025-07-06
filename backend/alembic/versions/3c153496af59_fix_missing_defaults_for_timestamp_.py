"""fix_missing_defaults_for_timestamp_columns

Revision ID: 3c153496af59
Revises: 44e9bb081149
Create Date: 2025-07-06 08:33:21.650472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c153496af59'
down_revision: Union[str, Sequence[str], None] = '44e9bb081149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fix missing default values for timestamp columns
    # These were manually fixed in production but need to be documented in migrations
    
    # Fix users.created_at default
    op.execute("ALTER TABLE users ALTER COLUMN created_at SET DEFAULT NOW();")
    
    # Fix email_syncs.created_at default
    op.execute("ALTER TABLE email_syncs ALTER COLUMN created_at SET DEFAULT NOW();")
    
    # Fix email_syncs.updated_at default
    op.execute("ALTER TABLE email_syncs ALTER COLUMN updated_at SET DEFAULT NOW();")
    
    # Fix email_operations.created_at default
    op.execute("ALTER TABLE email_operations ALTER COLUMN created_at SET DEFAULT NOW();")
    
    # Fix email_operations.updated_at default
    op.execute("ALTER TABLE email_operations ALTER COLUMN updated_at SET DEFAULT NOW();")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the default values we added
    op.execute("ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT;")
    op.execute("ALTER TABLE email_syncs ALTER COLUMN created_at DROP DEFAULT;")
    op.execute("ALTER TABLE email_syncs ALTER COLUMN updated_at DROP DEFAULT;")
    op.execute("ALTER TABLE email_operations ALTER COLUMN created_at DROP DEFAULT;")
    op.execute("ALTER TABLE email_operations ALTER COLUMN updated_at DROP DEFAULT;")
