"""add_sender_rule_metadata

Revision ID: d08fbd8d2dae
Revises: 84913d52fba2
Create Date: 2025-04-13 21:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'd08fbd8d2dae'
down_revision: Union[str, None] = '84913d52fba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add rule_metadata column to sender_rules table
    op.add_column('sender_rules', sa.Column('rule_metadata', postgresql.JSONB(), nullable=True))
    # Add created_at and updated_at columns with default values
    op.add_column('sender_rules', sa.Column('created_at', sa.DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('sender_rules', sa.Column('updated_at', sa.DateTime(), server_default=text('CURRENT_TIMESTAMP'), nullable=False))
    # Add trigger to automatically update updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_sender_rules_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_sender_rules_updated_at
            BEFORE UPDATE ON sender_rules
            FOR EACH ROW
            EXECUTE FUNCTION update_sender_rules_updated_at();
    """)


def downgrade() -> None:
    # Drop trigger and function first
    op.execute("""
        DROP TRIGGER IF EXISTS update_sender_rules_updated_at ON sender_rules;
        DROP FUNCTION IF EXISTS update_sender_rules_updated_at();
    """)
    # Drop columns
    op.drop_column('sender_rules', 'rule_metadata')
    op.drop_column('sender_rules', 'updated_at')
    op.drop_column('sender_rules', 'created_at')
