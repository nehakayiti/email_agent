"""update_categorization_feedback_table

Revision ID: 84913d52fba2
Revises: beb7229d1aa7
Create Date: 2024-04-13 19:00:27.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '84913d52fba2'
down_revision = 'beb7229d1aa7'
branch_labels = None
depends_on = None

def upgrade():
    # Drop old columns that are no longer needed
    op.drop_column('categorization_feedback', 'user_category')
    op.drop_column('categorization_feedback', 'feedback_source')
    op.drop_column('categorization_feedback', 'email_subject')
    op.drop_column('categorization_feedback', 'email_sender')
    op.drop_column('categorization_feedback', 'matched_keywords')
    op.drop_column('categorization_feedback', 'matched_sender_rules')
    
    # Add new columns
    op.add_column('categorization_feedback',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False)
    )
    op.add_column('categorization_feedback',
        sa.Column('new_category', sa.String(50), nullable=False)
    )
    op.add_column('categorization_feedback',
        sa.Column('feedback_timestamp', sa.DateTime(timezone=True), nullable=False)
    )
    op.add_column('categorization_feedback',
        sa.Column('feedback_metadata', postgresql.JSONB, nullable=True)
    )
    
    # Add foreign key constraint for user_id
    op.create_foreign_key(
        'categorization_feedback_user_id_fkey',
        'categorization_feedback', 'users',
        ['user_id'], ['id']
    )

def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('categorization_feedback_user_id_fkey', 'categorization_feedback', type_='foreignkey')
    
    # Remove new columns
    op.drop_column('categorization_feedback', 'user_id')
    op.drop_column('categorization_feedback', 'new_category')
    op.drop_column('categorization_feedback', 'feedback_timestamp')
    op.drop_column('categorization_feedback', 'feedback_metadata')
    
    # Add back old columns
    op.add_column('categorization_feedback',
        sa.Column('user_category', sa.String(50), nullable=True)
    )
    op.add_column('categorization_feedback',
        sa.Column('feedback_source', sa.String(20), nullable=True)
    )
    op.add_column('categorization_feedback',
        sa.Column('email_subject', sa.Text, nullable=True)
    )
    op.add_column('categorization_feedback',
        sa.Column('email_sender', sa.Text, nullable=True)
    )
    op.add_column('categorization_feedback',
        sa.Column('matched_keywords', postgresql.ARRAY(sa.Text), nullable=True)
    )
    op.add_column('categorization_feedback',
        sa.Column('matched_sender_rules', postgresql.ARRAY(sa.Text), nullable=True)
    )
