"""merge sync_details and main branch

Revision ID: d0e34b30ee79
Revises: be7f266c2199, auto_create_sync_details_table
Create Date: 2025-04-19 23:25:49.336505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0e34b30ee79'
down_revision: Union[str, None] = ('be7f266c2199', 'auto_create_sync_details_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
