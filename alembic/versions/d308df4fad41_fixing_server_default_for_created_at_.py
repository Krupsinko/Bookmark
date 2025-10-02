"""fixing server_default for created_at column

Revision ID: d308df4fad41
Revises: eab9e64aefa1
Create Date: 2025-10-02 23:19:31.021712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd308df4fad41'
down_revision: Union[str, Sequence[str], None] = 'eab9e64aefa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    with op.batch_alter_table("bookmark") as batch_op:
        batch_op.alter_column("created_at",
                        existing_type=sa.DateTime(),
                        existing_nullable=True,
                        server_default=sa.func.now())


def downgrade() -> None:
    with op.batch_alter_table("bookmark") as batch_op:
        batch_op.alter_column("created_at",
                        existing_type=sa.DateTime(),
                        existing_nullable=True,
                        server_default=None)
