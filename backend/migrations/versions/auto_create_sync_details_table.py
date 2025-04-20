from alembic import op
import sqlalchemy as sa
import enum

# revision identifiers, used by Alembic.
revision = 'auto_create_sync_details_table'
down_revision = None
branch_labels = None
depends_on = None

class SyncDirection(str, enum.Enum):
    GMAIL_TO_EA = 'Gmail → EA'
    EA_TO_GMAIL = 'EA → Gmail'
    BI_DIRECTIONAL = 'Bi-directional'

class SyncType(str, enum.Enum):
    MANUAL = 'Manual'
    AUTOMATIC = 'Automatic'

class SyncStatus(str, enum.Enum):
    SUCCESS = 'success'
    ERROR = 'error'

def upgrade():
    op.create_table(
        'sync_details',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), index=True, nullable=False),
        sa.Column('account_email', sa.String(), nullable=False),
        sa.Column('direction', sa.Enum(SyncDirection), nullable=False),
        sa.Column('sync_type', sa.Enum(SyncType), nullable=False),
        sa.Column('sync_started_at', sa.DateTime(), nullable=False),
        sa.Column('sync_completed_at', sa.DateTime(), nullable=False),
        sa.Column('duration_sec', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum(SyncStatus), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('emails_synced', sa.Integer(), nullable=False),
        sa.Column('changes_detected', sa.Integer(), nullable=False),
        sa.Column('changes_applied', sa.Integer(), nullable=False),
        sa.Column('pending_ea_changes', sa.JSON(), nullable=True),
        sa.Column('backend_version', sa.String(), nullable=True),
        sa.Column('data_freshness_sec', sa.Integer(), nullable=True),
    )

def downgrade():
    op.drop_table('sync_details') 