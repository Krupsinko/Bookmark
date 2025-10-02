"""fixing empty fields

Revision ID: 0bb33377cf88
Revises: d308df4fad41
Create Date: 2025-10-02 23:35:55.787363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bb33377cf88'
down_revision: Union[str, Sequence[str], None] = 'd308df4fad41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE bookmark SET created_at = updated_at")

def downgrade() -> None:
    op.execute("UPDATE bookmark SET updated_at = created_at")
