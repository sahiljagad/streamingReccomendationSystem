"""Add review_text to user_content

Revision ID: bb885ddc6164
Revises: 57b405ee1a59
Create Date: 2025-12-01 22:12:33.413325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb885ddc6164'
down_revision: Union[str, Sequence[str], None] = '57b405ee1a59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_content', sa.Column('review_text', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('user_content', 'review_text')
