"""unique constraint horarios dia semana

Revision ID: 41047a037c9e
Revises: f743e1b311f4
Create Date: 2026-07-24 15:38:07.894232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41047a037c9e'
down_revision: Union[str, Sequence[str], None] = 'f743e1b311f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        'ix_horarios_dia_semana_unique',
        'horarios',
        ['dia_semana'],
        unique=True,
        postgresql_where=sa.text('activo = true')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_horarios_dia_semana_unique', table_name='horarios')