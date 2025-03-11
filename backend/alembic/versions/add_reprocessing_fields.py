"""Add reprocessing fields to emails table

Revision ID: add_reprocessing_fields
Revises: remove_is_deleted_in_gmail
Create Date: 2025-03-10 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_reprocessing_fields'
down_revision = 'remove_is_deleted_in_gmail'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    # Add the new columns for email reprocessing
    op.add_column('emails', sa.Column('is_dirty', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('emails', sa.Column('last_reprocessed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Ensure all existing emails have is_dirty=false
    op.execute("""
        UPDATE emails 
        SET is_dirty = false
        WHERE is_dirty IS NULL;
    """)
    
    # Make is_dirty not nullable after setting default value
    op.alter_column('emails', 'is_dirty', nullable=False)


def downgrade():
    # Remove the columns added in the upgrade
    op.drop_column('emails', 'last_reprocessed_at')
    op.drop_column('emails', 'is_dirty') 