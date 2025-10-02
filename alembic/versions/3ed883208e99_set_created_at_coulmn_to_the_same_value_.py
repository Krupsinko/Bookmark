"""set created_at coulmn to the same value as updated_at

Revision ID: 3ed883208e99
Revises: d65efbda2994
Create Date: 2025-10-02 20:22:57.654769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ed883208e99'
down_revision: Union[str, Sequence[str], None] = 'd65efbda2994'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE bookmark SET created_at = updated_at")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE bookmark SET updated_at = created_at")
