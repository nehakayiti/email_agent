"""add_missing_columns_to_email_categorization_decisions

Revision ID: beb7229d1aa7
Revises: 4acf6e7a5bc4
Create Date: 2024-04-13 18:31:08.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'beb7229d1aa7'
down_revision = '4acf6e7a5bc4'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns to email_categorization_decisions table
    op.add_column('email_categorization_decisions',
        sa.Column('decision_type', sa.String(50), nullable=True)
    )
    op.add_column('email_categorization_decisions',
        sa.Column('decision_factors', postgresql.JSONB, nullable=True)
    )
    op.add_column('email_categorization_decisions',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

def downgrade():
    # Remove added columns
    op.drop_column('email_categorization_decisions', 'decision_type')
    op.drop_column('email_categorization_decisions', 'decision_factors')
    op.drop_column('email_categorization_decisions', 'updated_at')
