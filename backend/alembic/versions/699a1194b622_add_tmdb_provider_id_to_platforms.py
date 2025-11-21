"""Add tmdb_provider_id to platforms

Revision ID: 699a1194b622
Revises: 5547dc29a5df
Create Date: 2025-11-19 23:21:57.483763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '699a1194b622'
down_revision: Union[str, Sequence[str], None] = '5547dc29a5df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('platforms', sa.Column('tmdb_provider_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('platforms', 'tmdb_provider_id')
