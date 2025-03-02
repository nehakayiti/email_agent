"""Remove is_deleted_in_gmail column

Revision ID: remove_is_deleted_in_gmail
Revises: 
Create Date: 2025-03-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'remove_is_deleted_in_gmail'
down_revision = None  # Update this to the actual previous migration
branch_labels = None
depends_on = None


def upgrade():
    # First, ensure all emails that had is_deleted_in_gmail=true have the TRASH label
    op.execute("""
        UPDATE emails 
        SET 
            labels = CASE 
                WHEN is_deleted_in_gmail = true AND NOT (labels @> ARRAY['TRASH']) THEN 
                    array_append(COALESCE(labels, ARRAY[]::varchar[]), 'TRASH')
                ELSE 
                    labels
            END,
            category = CASE 
                WHEN is_deleted_in_gmail = true AND category != 'trash' THEN 
                    'trash'
                ELSE 
                    category
            END
        WHERE is_deleted_in_gmail = true;
    """)
    
    # Remove the is_deleted_in_gmail column
    op.drop_column('emails', 'is_deleted_in_gmail')


def downgrade():
    # Add the is_deleted_in_gmail column back
    op.add_column('emails', sa.Column('is_deleted_in_gmail', sa.Boolean(), nullable=True, server_default='false'))
    
    # Set is_deleted_in_gmail=true for emails with TRASH label
    op.execute("""
        UPDATE emails 
        SET is_deleted_in_gmail = true
        WHERE labels @> ARRAY['TRASH'];
    """) 