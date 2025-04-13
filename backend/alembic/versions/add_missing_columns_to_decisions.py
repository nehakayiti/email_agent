"""Add missing columns to email categorization decisions

Revision ID: add_missing_columns_to_decisions
Revises: remove_is_deleted_in_gmail
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'add_missing_columns_to_decisions'
down_revision = 'remove_is_deleted_in_gmail'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns
    op.add_column('email_categorization_decisions',
        sa.Column('decision_type', sa.String(50), nullable=True)
    )
    op.add_column('email_categorization_decisions',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

def downgrade():
    # Remove added columns
    op.drop_column('email_categorization_decisions', 'decision_type')
    op.drop_column('email_categorization_decisions', 'updated_at') 