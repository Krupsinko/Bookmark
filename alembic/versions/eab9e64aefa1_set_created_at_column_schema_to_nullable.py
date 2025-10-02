"""set created_at column schema to nullable 

Revision ID: eab9e64aefa1
Revises: 3ed883208e99
Create Date: 2025-10-02 22:54:49.424985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eab9e64aefa1'
down_revision: Union[str, Sequence[str], None] = '3ed883208e99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    with op.batch_alter_table("bookmark") as batch_op:
        batch_op.alter_column("created_at",
                              existing_type=sa.DateTime,
                              nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("bookmark") as batch_op:
        batch_op.alter_column("created_at",
                              existing_type=sa.DateTime(),
                              nullable=False)
