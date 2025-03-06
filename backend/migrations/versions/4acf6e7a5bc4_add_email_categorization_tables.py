"""add_email_categorization_tables

Revision ID: 4acf6e7a5bc4
Revises: 485846b5c9d0
Create Date: 2025-03-06 09:00:28.046348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4acf6e7a5bc4'
down_revision: Union[str, None] = '485846b5c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
