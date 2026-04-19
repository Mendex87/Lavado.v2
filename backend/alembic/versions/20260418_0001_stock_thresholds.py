"""add stock thresholds

Revision ID: 20260418_0001_stock_thresholds
Revises: 20260417_0001
Create Date: 2026-04-18 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '20260418_0001_stock_thresholds'
down_revision = '20260417_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('quarry_stock', sa.Column('threshold_low', sa.Numeric(14, 3), nullable=False, server_default='80.0'))
    op.add_column('quarry_stock', sa.Column('threshold_critical', sa.Numeric(14, 3), nullable=False, server_default='40.0'))


def downgrade() -> None:
    op.drop_column('quarry_stock', 'threshold_critical')
    op.drop_column('quarry_stock', 'threshold_low')