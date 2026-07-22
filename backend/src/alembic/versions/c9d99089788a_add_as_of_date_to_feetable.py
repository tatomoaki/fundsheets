"""Add as_of_date to FeeTable

Revision ID: c9d99089788a
Revises: fc690c8d38cc
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d99089788a'
down_revision: Union[str, Sequence[str], None] = 'fc690c8d38cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('fees', sa.Column('as_of_date', sa.Date(), nullable=True))
    # Backfill existing rows: best-effort, since as_of_date wasn't captured
    # separately before. effective_date is the closest available proxy.
    op.execute("UPDATE fees SET as_of_date = effective_date WHERE as_of_date IS NULL")
    op.alter_column('fees', 'as_of_date', nullable=False)

    op.create_index(op.f('ix_fees_as_of_date'), 'fees', ['as_of_date'], unique=False)

    op.drop_constraint('uq_fee_fund_effective_date', 'fees', type_='unique')
    op.create_unique_constraint('uq_fee_fund_as_of_date', 'fees', ['fund_id', 'as_of_date'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_fee_fund_as_of_date', 'fees', type_='unique')
    op.create_unique_constraint('uq_fee_fund_effective_date', 'fees', ['fund_id', 'effective_date'])

    op.drop_index(op.f('ix_fees_as_of_date'), table_name='fees')
    op.drop_column('fees', 'as_of_date')
