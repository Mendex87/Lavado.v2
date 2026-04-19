"""add handover tables

Revision ID: 20260418_0002_handover
Revises: 20260418_0001_stock_thresholds
Create Date: 2026-04-18 14:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '20260418_0002_handover'
down_revision = '20260418_0001_stock_thresholds'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'handover_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('from_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('to_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('from_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=True),
        sa.Column('to_shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=True),
        sa.Column('handover_started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('handover_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('process_summary_json', sa.JSON(), nullable=True),
        sa.Column('stock_summary_json', sa.JSON(), nullable=True),
        sa.Column('pending_issues_json', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_handover_records_status', 'handover_records', ['status'])
    op.create_index('idx_handover_records_datetime', 'handover_records', ['handover_started_at'])
    
    op.create_table(
        'handover_checklist_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('handover_id', sa.Integer(), sa.ForeignKey('handover_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_text', sa.String(), nullable=False),
        sa.Column('checked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('handover_checklist_items')
    op.drop_index('idx_handover_records_datetime', table_name='handover_records')
    op.drop_index('idx_handover_records_status', table_name='handover_records')
    op.drop_table('handover_records')