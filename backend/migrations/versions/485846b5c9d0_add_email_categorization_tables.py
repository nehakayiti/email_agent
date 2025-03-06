"""add_email_categorization_tables

Revision ID: 485846b5c9d0
Revises: 
Create Date: 2025-03-06 08:54:50.221715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '485846b5c9d0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create email_categories table
    op.create_table(
        'email_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True, default=50),
        sa.Column('is_system', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'is_system', name='uq_category_name_system')
    )
    op.create_index('idx_email_category_name', 'email_categories', ['name'])
    
    # Create category_keywords table
    op.create_table(
        'category_keywords',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(), nullable=False),
        sa.Column('is_regex', sa.Boolean(), nullable=True, default=False),
        sa.Column('weight', sa.Integer(), nullable=True, default=1),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['email_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_category_keyword', 'category_keywords', ['keyword'])
    op.create_index('idx_category_keyword_category', 'category_keywords', ['category_id'])
    op.create_index('idx_category_keyword_user', 'category_keywords', ['user_id'])
    
    # Create sender_rules table
    op.create_table(
        'sender_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('is_domain', sa.Boolean(), nullable=True, default=True),
        sa.Column('weight', sa.Integer(), nullable=True, default=1),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['email_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sender_rule_pattern', 'sender_rules', ['pattern'])
    op.create_index('idx_sender_rule_category', 'sender_rules', ['category_id'])
    op.create_index('idx_sender_rule_user', 'sender_rules', ['user_id'])


def downgrade() -> None:
    op.drop_table('sender_rules')
    op.drop_table('category_keywords')
    op.drop_table('email_categories')
