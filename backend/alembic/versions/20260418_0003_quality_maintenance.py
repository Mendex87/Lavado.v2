"""add quality maintenance reporting modules

Revision ID: 20260418_0003_quality_maintenance
Revises: 20260418_0002_handover
Create Date: 2026-04-18 15:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '20260418_0003_quality_maintenance'
down_revision = '20260418_0002_handover'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'quality_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('process_id', sa.Integer(), sa.ForeignKey('processes.id'), nullable=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('quarry_id', sa.Integer(), sa.ForeignKey('quarries.id'), nullable=True),
        sa.Column('sample_code', sa.String(), nullable=False),
        sa.Column('sample_type', sa.String(), nullable=False),
        sa.Column('mesh_20', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_40', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_80', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_120', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_200', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_fines', sa.Numeric(5, 2), nullable=True),
        sa.Column('humidity_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('density', sa.Numeric(6, 3), nullable=True),
        sa.Column('visual_inspection', sa.Text(), nullable=True),
        sa.Column('result_status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('sampled_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('analyzed_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('sampled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'quality_specifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('mesh_20_min', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_20_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_40_min', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_40_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_80_min', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_80_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_120_min', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_120_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_200_min', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_200_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('mesh_fines_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('humidity_max', sa.Numeric(5, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'lot_traceability',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lot_number', sa.String(), nullable=False),
        sa.Column('process_id', sa.Integer(), sa.ForeignKey('processes.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('total_ton', sa.Numeric(14, 3), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='in_progress'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('lot_number', name='uq_lot_number'),
    )

    op.create_table(
        'maintenance_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_code', sa.String(), nullable=False),
        sa.Column('request_type', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='open'),
        sa.Column('line_id', sa.Integer(), sa.ForeignKey('lines.id'), nullable=True),
        sa.Column('belt_id', sa.Integer(), sa.ForeignKey('belts.id'), nullable=True),
        sa.Column('scale_id', sa.Integer(), sa.ForeignKey('scales.id'), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reported_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('in_progress_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.UniqueConstraint('request_code', name='uq_request_code'),
    )

    op.create_table(
        'maintenance_incidents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('incident_code', sa.String(), nullable=False),
        sa.Column('maintenance_request_id', sa.Integer(), sa.ForeignKey('maintenance_requests.id'), nullable=True),
        sa.Column('process_id', sa.Integer(), sa.ForeignKey('processes.id'), nullable=True),
        sa.Column('line_id', sa.Integer(), sa.ForeignKey('lines.id'), nullable=True),
        sa.Column('incident_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('downtime_minutes', sa.Numeric(6, 2), nullable=True),
        sa.Column('production_loss_ton', sa.Numeric(14, 3), nullable=True),
        sa.Column('reported_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('resolved_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.UniqueConstraint('incident_code', name='uq_incident_code'),
    )

    op.create_table(
        'preventive_maintenance_tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_code', sa.String(), nullable=False),
        sa.Column('equipment_type', sa.String(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), sa.ForeignKey('belts.id'), nullable=True),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('frequency_days', sa.Integer(), nullable=False),
        sa.Column('last_performed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('task_code', name='uq_task_code'),
    )

    op.create_table(
        'daily_reports',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('report_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('shift_id', sa.Integer(), sa.ForeignKey('shifts.id'), nullable=True),
        sa.Column('line_id', sa.Integer(), sa.ForeignKey('lines.id'), nullable=True),
        sa.Column('total_input_ton', sa.Numeric(14, 3), nullable=False, server_default='0'),
        sa.Column('total_product_a_ton', sa.Numeric(14, 3), nullable=False, server_default='0'),
        sa.Column('total_product_b_ton', sa.Numeric(14, 3), nullable=False, server_default='0'),
        sa.Column('total_discard_ton', sa.Numeric(14, 3), nullable=False, server_default='0'),
        sa.Column('avg_feed_rate_tph', sa.Numeric(7, 2), nullable=True),
        sa.Column('total_production_hours', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('downtime_minutes', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('alarm_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quality_samples_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'oee_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('line_id', sa.Integer(), sa.ForeignKey('lines.id'), nullable=False),
        sa.Column('snapshot_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('snapshot_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('availability_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('performance_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('quality_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('oee_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('planned_production_minutes', sa.Numeric(6, 2), nullable=False),
        sa.Column('actual_production_minutes', sa.Numeric(6, 2), nullable=False),
        sa.Column('ideal_cycle_time_minutes', sa.Numeric(6, 2), nullable=False),
        sa.Column('total_output_ton', sa.Numeric(14, 3), nullable=False),
        sa.Column('good_output_ton', sa.Numeric(14, 3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'energy_readings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('line_id', sa.Integer(), sa.ForeignKey('lines.id'), nullable=True),
        sa.Column('meter_id', sa.String(), nullable=False),
        sa.Column('reading_type', sa.String(), nullable=False),
        sa.Column('kwh_value', sa.Numeric(12, 2), nullable=False),
        sa.Column('power_kw', sa.Numeric(8, 2), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('idx_quality_records_process', 'quality_records', ['process_id'])
    op.create_index('idx_quality_records_status', 'quality_records', ['result_status'])
    op.create_index('idx_lot_traceability_process', 'lot_traceability', ['process_id'])
    op.create_index('idx_maintenance_requests_status', 'maintenance_requests', ['status'])
    op.create_index('idx_maintenance_requests_priority', 'maintenance_requests', ['priority'])
    op.create_index('idx_maintenance_incidents_line', 'maintenance_incidents', ['line_id'])
    op.create_index('idx_daily_reports_date', 'daily_reports', ['report_date'])
    op.create_index('idx_oee_snapshots_line', 'oee_snapshots', ['line_id'])
    op.create_index('idx_energy_readings_line', 'energy_readings', ['line_id'])


def downgrade() -> None:
    op.drop_index('idx_energy_readings_line', table_name='energy_readings')
    op.drop_index('idx_oee_snapshots_line', table_name='oee_snapshots')
    op.drop_index('idx_daily_reports_date', table_name='daily_reports')
    op.drop_index('idx_maintenance_incidents_line', table_name='maintenance_incidents')
    op.drop_index('idx_maintenance_requests_priority', table_name='maintenance_requests')
    op.drop_index('idx_maintenance_requests_status', table_name='maintenance_requests')
    op.drop_index('idx_lot_traceability_process', table_name='lot_traceability')
    op.drop_index('idx_quality_records_status', table_name='quality_records')
    op.drop_index('idx_quality_records_process', table_name='quality_records')
    op.drop_table('energy_readings')
    op.drop_table('oee_snapshots')
    op.drop_table('daily_reports')
    op.drop_table('preventive_maintenance_tasks')
    op.drop_table('maintenance_incidents')
    op.drop_table('maintenance_requests')
    op.drop_table('lot_traceability')
    op.drop_table('quality_specifications')
    op.drop_table('quality_records')