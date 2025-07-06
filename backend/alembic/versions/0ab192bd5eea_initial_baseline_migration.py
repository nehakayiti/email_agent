"""Initial baseline migration

Revision ID: 0ab192bd5eea
Revises: 
Create Date: 2025-07-05 19:35:56.144784

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0ab192bd5eea'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enums for sync_details
    syncdirection = sa.Enum('GMAIL_TO_EA', 'EA_TO_GMAIL', 'BI_DIRECTIONAL', name='syncdirection')
    synctype = sa.Enum('MANUAL', 'AUTOMATIC', name='synctype')
    syncstatus = sa.Enum('SUCCESS', 'ERROR', name='syncstatus')

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_sign_in', sa.DateTime(timezone=True)),
        sa.Column('credentials', sa.JSON()),
    )

    # Email categories
    op.create_table(
        'email_categories',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('priority', sa.Integer(), default=50),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
        sa.UniqueConstraint('name', 'is_system', name='uq_category_name_system'),
    )
    op.create_index('idx_email_category_name', 'email_categories', ['name'])

    # Category keywords
    op.create_table(
        'category_keywords',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('email_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('keyword', sa.String(), nullable=False),
        sa.Column('is_regex', sa.Boolean(), default=False),
        sa.Column('weight', sa.Integer(), default=1),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
    )
    op.create_index('idx_category_keyword', 'category_keywords', ['keyword'])
    op.create_index('idx_category_keyword_category', 'category_keywords', ['category_id'])
    op.create_index('idx_category_keyword_user', 'category_keywords', ['user_id'])

    # Sender rules
    op.create_table(
        'sender_rules',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('email_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('is_domain', sa.Boolean(), default=True),
        sa.Column('weight', sa.Integer(), default=1),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('rule_metadata', sa.JSON(), nullable=True),
        sa.UniqueConstraint('pattern', 'is_domain', 'user_id', name='unique_sender_rule_per_domain'),
    )

    # Emails
    op.create_table(
        'emails',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('gmail_id', sa.String(), nullable=False),
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('subject', sa.String()),
        sa.Column('from_email', sa.String()),
        sa.Column('received_at', sa.DateTime(timezone=True)),
        sa.Column('snippet', sa.String()),
        sa.Column('labels', postgresql.ARRAY(sa.String())),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('is_processed', sa.Boolean(), default=False),
        sa.Column('importance_score', sa.Integer()),
        sa.Column('category', sa.String()),
        sa.Column('raw_data', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_dirty', sa.Boolean(), default=False),
        sa.Column('last_reprocessed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_emails_user_id_received_at', 'emails', ['user_id', 'received_at'])
    op.create_index('ix_emails_gmail_id', 'emails', ['gmail_id'])
    op.create_index('ix_emails_category', 'emails', ['category'])

    # Categorization feedback
    op.create_table(
        'categorization_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('email_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emails.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('original_category', sa.String()),
        sa.Column('new_category', sa.String(), nullable=False),
        sa.Column('feedback_timestamp', sa.DateTime(), nullable=False),
        sa.Column('feedback_metadata', sa.JSON()),
    )

    # Email categorization decisions
    op.create_table(
        'email_categorization_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('email_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emails.id'), nullable=False),
        sa.Column('category_to', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('decision_factors', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Email operations
    op.create_table(
        'email_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emails.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('operation_data', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('retries', sa.Integer(), default=0),
    )
    op.create_index('ix_email_operations_status', 'email_operations', ['status'])
    op.create_index('ix_email_operations_user_id', 'email_operations', ['user_id'])
    op.create_index('ix_email_operations_email_id', 'email_operations', ['email_id'])
    op.create_index('ix_email_operations_created_at', 'email_operations', ['created_at'])
    op.create_index('ix_email_operations_operation_type', 'email_operations', ['operation_type'])

    # Email trash events
    op.create_table(
        'email_trash_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emails.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('sender_email', sa.String(), nullable=False),
        sa.Column('sender_domain', sa.String(), nullable=False),
        sa.Column('subject', sa.String()),
        sa.Column('snippet', sa.Text()),
        sa.Column('keywords', postgresql.ARRAY(sa.String())),
        sa.Column('is_auto_categorized', sa.Boolean(), default=False),
        sa.Column('categorization_source', sa.String(20)),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('email_metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_email_trash_events_user_id', 'email_trash_events', ['user_id'])
    op.create_index('ix_email_trash_events_email_id', 'email_trash_events', ['email_id'])
    op.create_index('ix_email_trash_events_event_type', 'email_trash_events', ['event_type'])
    op.create_index('ix_email_trash_events_sender_domain', 'email_trash_events', ['sender_domain'])
    op.create_index('ix_email_trash_events_created_at', 'email_trash_events', ['created_at'])
    op.create_index('ix_email_trash_events_categorization_source', 'email_trash_events', ['categorization_source'])

    # Email syncs
    op.create_table(
        'email_syncs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('last_fetched_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_history_id', sa.String()),
        sa.Column('sync_cadence', sa.Integer(), nullable=False, default=60),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_email_syncs_user_id', 'email_syncs', ['user_id'])
    op.create_index('ix_email_syncs_last_fetched_at', 'email_syncs', ['last_fetched_at'])

    # Sync details
    op.create_table(
        'sync_details',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), index=True, nullable=False),
        sa.Column('account_email', sa.String(), nullable=False),
        sa.Column('direction', syncdirection, nullable=False),
        sa.Column('sync_type', synctype, nullable=False),
        sa.Column('sync_started_at', sa.DateTime(), nullable=False),
        sa.Column('sync_completed_at', sa.DateTime(), nullable=False),
        sa.Column('duration_sec', sa.Float(), nullable=False),
        sa.Column('status', syncstatus, nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('emails_synced', sa.Integer(), nullable=False),
        sa.Column('changes_detected', sa.Integer(), nullable=False),
        sa.Column('changes_applied', sa.Integer(), nullable=False),
        sa.Column('pending_ea_changes', sa.JSON(), nullable=True),
        sa.Column('backend_version', sa.String(), nullable=True),
        sa.Column('data_freshness_sec', sa.Integer(), nullable=True),
    )

def downgrade() -> None:
    op.drop_index('ix_sync_details_user_id', table_name='sync_details')
    op.drop_table('sync_details')
    op.drop_index('ix_email_syncs_last_fetched_at', table_name='email_syncs')
    op.drop_index('ix_email_syncs_user_id', table_name='email_syncs')
    op.drop_table('email_syncs')
    op.drop_index('ix_email_trash_events_categorization_source', table_name='email_trash_events')
    op.drop_index('ix_email_trash_events_created_at', table_name='email_trash_events')
    op.drop_index('ix_email_trash_events_sender_domain', table_name='email_trash_events')
    op.drop_index('ix_email_trash_events_event_type', table_name='email_trash_events')
    op.drop_index('ix_email_trash_events_email_id', table_name='email_trash_events')
    op.drop_index('ix_email_trash_events_user_id', table_name='email_trash_events')
    op.drop_table('email_trash_events')
    op.drop_index('ix_email_operations_operation_type', table_name='email_operations')
    op.drop_index('ix_email_operations_created_at', table_name='email_operations')
    op.drop_index('ix_email_operations_email_id', table_name='email_operations')
    op.drop_index('ix_email_operations_user_id', table_name='email_operations')
    op.drop_index('ix_email_operations_status', table_name='email_operations')
    op.drop_table('email_operations')
    op.drop_table('email_categorization_decisions')
    op.drop_table('categorization_feedback')
    op.drop_index('ix_emails_category', table_name='emails')
    op.drop_index('ix_emails_gmail_id', table_name='emails')
    op.drop_index('ix_emails_user_id_received_at', table_name='emails')
    op.drop_table('emails')
    op.drop_table('sender_rules')
    op.drop_index('idx_category_keyword_user', table_name='category_keywords')
    op.drop_index('idx_category_keyword_category', table_name='category_keywords')
    op.drop_index('idx_category_keyword', table_name='category_keywords')
    op.drop_table('category_keywords')
    op.drop_index('idx_email_category_name', table_name='email_categories')
    op.drop_table('email_categories')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS syncdirection')
    op.execute('DROP TYPE IF EXISTS synctype')
    op.execute('DROP TYPE IF EXISTS syncstatus')
