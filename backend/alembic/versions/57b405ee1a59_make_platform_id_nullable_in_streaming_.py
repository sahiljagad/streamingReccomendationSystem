"""Make platform_id nullable in streaming_availability

Revision ID: 57b405ee1a59
Revises: 699a1194b622
Create Date: 2025-11-20 22:33:16.271673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57b405ee1a59'
down_revision: Union[str, Sequence[str], None] = '699a1194b622'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table('streaming_availability', schema=None) as batch_op:
        batch_op.alter_column('platform_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)


def downgrade():
    with op.batch_alter_table('streaming_availability', schema=None) as batch_op:
        batch_op.alter_column('platform_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)