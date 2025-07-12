"""add_attention_score_to_emails

Revision ID: 25a3fecf7f7e
Revises: dbefe17cedc1
Create Date: 2025-07-12 14:31:12.872679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25a3fecf7f7e'
down_revision: Union[str, Sequence[str], None] = 'dbefe17cedc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add attention_score column to emails table
    op.add_column('emails', sa.Column('attention_score', sa.Float(), nullable=False, server_default='0.0'))
    
    # Create index for efficient querying by attention score
    op.create_index('ix_emails_attention_score', 'emails', ['attention_score'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the index first
    op.drop_index('ix_emails_attention_score', table_name='emails')
    
    # Drop the attention_score column
    op.drop_column('emails', 'attention_score')
