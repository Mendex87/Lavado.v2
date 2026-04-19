-- Proyecto planta de lavado de arena de fracking
-- Esquema base v1.1
-- Objetivo: núcleo sólido, relacional, auditable y escalable
-- Motor objetivo: PostgreSQL

BEGIN;

-- =========================
-- Catálogos y seguridad
-- =========================

CREATE TABLE roles (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id         BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, role_id)
);

CREATE TABLE shifts (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id),
    shift_id            BIGINT REFERENCES shifts(id),
    login_at            TIMESTAMPTZ NOT NULL,
    logout_at           TIMESTAMPTZ,
    auth_source         TEXT NOT NULL DEFAULT 'app',
    device_label        TEXT,
    app_version         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Handover de Turno
-- =========================

CREATE TABLE handover_records (
    id                          BIGSERIAL PRIMARY KEY,
    from_user_id                BIGINT NOT NULL REFERENCES users(id),
    to_user_id                  BIGINT NOT NULL REFERENCES users(id),
    from_shift_id               BIGINT REFERENCES shifts(id),
    to_shift_id                 BIGINT REFERENCES shifts(id),
    handover_started_at         TIMESTAMPTZ NOT NULL,
    handover_completed_at       TIMESTAMPTZ,
    status                      TEXT NOT NULL DEFAULT 'pending',
    process_summary_json       JSONB,
    stock_summary_json          JSONB,
    pending_issues_json          JSONB,
    notes                       TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status IN ('pending', 'completed', 'cancelled'))
);

CREATE TABLE handover_checklist_items (
    id                      BIGSERIAL PRIMARY KEY,
    handover_id             BIGINT NOT NULL REFERENCES handover_records(id) ON DELETE CASCADE,
    item_text               TEXT NOT NULL,
    checked                 BOOLEAN NOT NULL DEFAULT FALSE,
    checked_at              TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_handover_records_status ON handover_records(status);
CREATE INDEX idx_handover_records_datetime ON handover_records(handover_started_at DESC);

-- =========================
-- Estructura de planta
-- =========================

CREATE TABLE lines (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quarries (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    mesh_label      TEXT,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quarry_products (
    id              BIGSERIAL PRIMARY KEY,
    quarry_id       BIGINT NOT NULL REFERENCES quarries(id),
    product_id      BIGINT NOT NULL REFERENCES products(id),
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (quarry_id, product_id)
);

CREATE TABLE belts (
    id              BIGSERIAL PRIMARY KEY,
    line_id         BIGINT REFERENCES lines(id),
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    purpose         TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scales (
    id              BIGSERIAL PRIMARY KEY,
    belt_id         BIGINT REFERENCES belts(id),
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    scale_kind      TEXT NOT NULL,
    plc_tag_prefix  TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (scale_kind IN ('entry', 'output', 'configurable_output'))
);

-- =========================
-- Procesos
-- =========================

CREATE TABLE processes (
    id                          BIGSERIAL PRIMARY KEY,
    code                        TEXT NOT NULL UNIQUE,
    line_id                     BIGINT NOT NULL REFERENCES lines(id),
    shift_id                    BIGINT NOT NULL REFERENCES shifts(id),
    shift_code_snapshot         TEXT NOT NULL,
    shift_name_snapshot         TEXT NOT NULL,
    shift_start_time_snapshot   TIME NOT NULL,
    shift_end_time_snapshot     TIME NOT NULL,
    operator_user_id            BIGINT NOT NULL REFERENCES users(id),
    supervisor_user_id          BIGINT REFERENCES users(id),
    user_session_id             BIGINT REFERENCES user_sessions(id),
    mode                        TEXT NOT NULL,
    status                      TEXT NOT NULL,
    started_at                  TIMESTAMPTZ NOT NULL,
    ended_at                    TIMESTAMPTZ,
    closed_by_user_id           BIGINT REFERENCES users(id),
    close_reason                TEXT,
    cancel_reason               TEXT,
    notes                       TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (mode IN ('simple', 'blend')),
    CHECK (status IN ('active', 'closed', 'cancelled')),
    CHECK ((status <> 'closed') OR ended_at IS NOT NULL),
    CHECK ((status <> 'cancelled') OR ended_at IS NOT NULL)
);

CREATE UNIQUE INDEX uq_process_one_active_per_line
ON processes(line_id)
WHERE status = 'active';

CREATE TABLE process_inputs (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    quarry_id               BIGINT NOT NULL REFERENCES quarries(id),
    scale_id                BIGINT REFERENCES scales(id),
    input_order             SMALLINT NOT NULL,
    hopper_code             TEXT,
    blend_target_pct        NUMERIC(5,2),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (input_order >= 1),
    CHECK (blend_target_pct IS NULL OR (blend_target_pct >= 0 AND blend_target_pct <= 100)),
    UNIQUE (process_id, input_order),
    UNIQUE (process_id, hopper_code)
);

CREATE TABLE process_outputs (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    scale_id                BIGINT REFERENCES scales(id),
    product_id              BIGINT REFERENCES products(id),
    output_code             TEXT NOT NULL,
    classification          TEXT NOT NULL,
    expected_humidity_pct   NUMERIC(5,2),
    humidity_source         TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (classification IN ('product', 'discard')),
    CHECK (expected_humidity_pct IS NULL OR (expected_humidity_pct >= 0 AND expected_humidity_pct <= 100)),
    CHECK (humidity_source IS NULL OR humidity_source IN ('manual', 'sensor', 'lab', 'estimated')),
    UNIQUE (process_id, output_code)
);

-- =========================
-- Producción y lecturas
-- =========================

CREATE TABLE process_scale_resets (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    requested_by_user_id    BIGINT NOT NULL REFERENCES users(id),
    confirmed_at            TIMESTAMPTZ NOT NULL,
    plc_ack_at              TIMESTAMPTZ,
    status                  TEXT NOT NULL DEFAULT 'requested',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status IN ('requested', 'acknowledged', 'failed'))
);

CREATE TABLE scale_totalizer_history (
    id                      BIGSERIAL PRIMARY KEY,
    scale_id                BIGINT NOT NULL REFERENCES scales(id),
    reading_at              TIMESTAMPTZ NOT NULL,
    totalizer_ton           NUMERIC(14,3) NOT NULL,
    source                  TEXT NOT NULL DEFAULT 'plc',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (scale_id, reading_at)
);

CREATE TABLE process_scale_readings (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    scale_id                BIGINT NOT NULL REFERENCES scales(id),
    reading_at              TIMESTAMPTZ NOT NULL,
    partial_ton             NUMERIC(14,3) NOT NULL,
    totalizer_ton           NUMERIC(14,3),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (process_id, scale_id, reading_at)
);

CREATE TABLE process_production_summary (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    process_output_id       BIGINT REFERENCES process_outputs(id) ON DELETE SET NULL,
    scale_id                BIGINT NOT NULL REFERENCES scales(id),
    product_id              BIGINT REFERENCES products(id),
    classification          TEXT NOT NULL,
    wet_ton                 NUMERIC(14,3) NOT NULL DEFAULT 0,
    humidity_pct            NUMERIC(5,2),
    humidity_source         TEXT,
    dry_ton                 NUMERIC(14,3),
    summarized_at           TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (classification IN ('product', 'discard')),
    CHECK (humidity_pct IS NULL OR (humidity_pct >= 0 AND humidity_pct <= 100)),
    CHECK (humidity_source IS NULL OR humidity_source IN ('manual', 'sensor', 'lab', 'estimated'))
);

-- =========================
-- Stock
-- =========================

CREATE TABLE quarry_stock (
    id                      BIGSERIAL PRIMARY KEY,
    quarry_id               BIGINT NOT NULL UNIQUE REFERENCES quarries(id) ON DELETE CASCADE,
    current_ton             NUMERIC(14,3) NOT NULL DEFAULT 0,
    threshold_low           NUMERIC(14,3) NOT NULL DEFAULT 80.0,
    threshold_critical      NUMERIC(14,3) NOT NULL DEFAULT 40.0,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quarry_stock_movements (
    id                      BIGSERIAL PRIMARY KEY,
    quarry_id               BIGINT NOT NULL REFERENCES quarries(id),
    process_id              BIGINT REFERENCES processes(id),
    scale_id                BIGINT REFERENCES scales(id),
    movement_type           TEXT NOT NULL,
    direction               TEXT NOT NULL,
    quantity_ton            NUMERIC(14,3) NOT NULL,
    signed_quantity_ton     NUMERIC(14,3) NOT NULL,
    source                  TEXT NOT NULL DEFAULT 'manual',
    reference_code          TEXT,
    entered_by_user_id      BIGINT NOT NULL REFERENCES users(id),
    reason                  TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (movement_type IN ('input', 'consumption', 'adjustment')),
    CHECK (direction IN ('in', 'out')),
    CHECK (quantity_ton >= 0),
    CHECK (
        (direction = 'in' AND signed_quantity_ton >= 0) OR
        (direction = 'out' AND signed_quantity_ton <= 0)
    ),
    CHECK (source IN ('manual', 'plc', 'integration', 'system'))
);

-- =========================
-- PLC / integración
-- =========================

CREATE TABLE plc_variables (
    id                      BIGSERIAL PRIMARY KEY,
    code                    TEXT NOT NULL UNIQUE,
    name                    TEXT NOT NULL,
    direction               TEXT NOT NULL,
    data_type               TEXT NOT NULL,
    description             TEXT,
    line_id                 BIGINT REFERENCES lines(id),
    scale_id                BIGINT REFERENCES scales(id),
    store_history           BOOLEAN NOT NULL DEFAULT FALSE,
    history_policy          TEXT,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (direction IN ('plc_to_app', 'app_to_plc')),
    CHECK (history_policy IS NULL OR history_policy IN ('on_change', 'periodic', 'critical_only'))
);

CREATE TABLE plc_variable_history (
    id                      BIGSERIAL PRIMARY KEY,
    plc_variable_id         BIGINT NOT NULL REFERENCES plc_variables(id) ON DELETE CASCADE,
    value_text              TEXT NOT NULL,
    captured_at             TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Eventos, alarmas y auditoría
-- =========================

CREATE TABLE process_events (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    user_id                 BIGINT REFERENCES users(id),
    event_type              TEXT NOT NULL,
    severity                TEXT NOT NULL,
    message                 TEXT NOT NULL,
    payload_json            JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (severity IN ('info', 'warning', 'critical'))
);

CREATE TABLE alarms (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT REFERENCES processes(id),
    line_id                 BIGINT REFERENCES lines(id),
    alarm_type              TEXT NOT NULL,
    severity                TEXT NOT NULL,
    message                 TEXT NOT NULL,
    started_at              TIMESTAMPTZ NOT NULL,
    ended_at                TIMESTAMPTZ,
    acknowledged_by_user_id BIGINT REFERENCES users(id),
    acknowledged_at         TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (severity IN ('info', 'warning', 'critical'))
);

CREATE TABLE audit_log (
    id                      BIGSERIAL PRIMARY KEY,
    user_id                 BIGINT REFERENCES users(id),
    entity_name             TEXT NOT NULL,
    entity_id               TEXT NOT NULL,
    action                  TEXT NOT NULL,
    before_json             JSONB,
    after_json              JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Soporte futuro
-- =========================

CREATE TABLE humidity_sensor_readings (
    id                      BIGSERIAL PRIMARY KEY,
    process_output_id       BIGINT REFERENCES process_outputs(id) ON DELETE CASCADE,
    product_id              BIGINT REFERENCES products(id),
    sensor_code             TEXT NOT NULL,
    humidity_pct            NUMERIC(5,2) NOT NULL,
    measured_at             TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (humidity_pct >= 0 AND humidity_pct <= 100)
);

CREATE TABLE quarry_yield_snapshots (
    id                      BIGSERIAL PRIMARY KEY,
    quarry_id               BIGINT NOT NULL REFERENCES quarries(id),
    process_id              BIGINT REFERENCES processes(id),
    input_ton               NUMERIC(14,3) NOT NULL,
    output_wet_ton          NUMERIC(14,3) NOT NULL,
    output_dry_ton          NUMERIC(14,3),
    yield_pct               NUMERIC(7,3),
    calculated_at           TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Calidad y trazabilidad
-- =========================

CREATE TABLE quality_records (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT REFERENCES processes(id),
    product_id              BIGINT REFERENCES products(id),
    quarry_id               BIGINT REFERENCES quarries(id),
    sample_code             TEXT NOT NULL,
    sample_type             TEXT NOT NULL,
    mesh_20                 NUMERIC(5,2),
    mesh_40                 NUMERIC(5,2),
    mesh_80                 NUMERIC(5,2),
    mesh_120                NUMERIC(5,2),
    mesh_200                NUMERIC(5,2),
    mesh_fines              NUMERIC(5,2),
    humidity_pct            NUMERIC(5,2),
    density                 NUMERIC(6,3),
    visual_inspection       TEXT,
    result_status           TEXT NOT NULL DEFAULT 'pending',
    sampled_by_user_id      BIGINT REFERENCES users(id),
    analyzed_by_user_id     BIGINT REFERENCES users(id),
    sampled_at              TIMESTAMPTZ,
    analyzed_at             TIMESTAMPTZ,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quality_specifications (
    id                      BIGSERIAL PRIMARY KEY,
    product_id              BIGINT NOT NULL REFERENCES products(id),
    mesh_20_min             NUMERIC(5,2),
    mesh_20_max             NUMERIC(5,2),
    mesh_40_min             NUMERIC(5,2),
    mesh_40_max             NUMERIC(5,2),
    mesh_80_min             NUMERIC(5,2),
    mesh_80_max             NUMERIC(5,2),
    mesh_120_min            NUMERIC(5,2),
    mesh_120_max            NUMERIC(5,2),
    mesh_200_min            NUMERIC(5,2),
    mesh_200_max            NUMERIC(5,2),
    mesh_fines_max          NUMERIC(5,2),
    humidity_max            NUMERIC(5,2),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE lot_traceability (
    id                      BIGSERIAL PRIMARY KEY,
    lot_number              TEXT NOT NULL UNIQUE,
    process_id              BIGINT NOT NULL REFERENCES processes(id),
    product_id              BIGINT NOT NULL REFERENCES products(id),
    total_ton               NUMERIC(14,3) NOT NULL,
    start_time              TIMESTAMPTZ NOT NULL,
    end_time                TIMESTAMPTZ,
    status                  TEXT NOT NULL DEFAULT 'in_progress',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Mantenimiento
-- =========================

CREATE TABLE maintenance_requests (
    id                      BIGSERIAL PRIMARY KEY,
    request_code            TEXT NOT NULL UNIQUE,
    request_type            TEXT NOT NULL,
    priority                TEXT NOT NULL,
    status                  TEXT NOT NULL DEFAULT 'open',
    line_id                 BIGINT REFERENCES lines(id),
    belt_id                 BIGINT REFERENCES belts(id),
    scale_id                BIGINT REFERENCES scales(id),
    description             TEXT NOT NULL,
    reported_by_user_id     BIGINT NOT NULL REFERENCES users(id),
    assigned_to_user_id     BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL,
    acknowledged_at         TIMESTAMPTZ,
    in_progress_at          TIMESTAMPTZ,
    completed_at            TIMESTAMPTZ,
    resolution_notes        TEXT
);

CREATE TABLE maintenance_incidents (
    id                      BIGSERIAL PRIMARY KEY,
    incident_code           TEXT NOT NULL UNIQUE,
    maintenance_request_id  BIGINT REFERENCES maintenance_requests(id),
    process_id              BIGINT REFERENCES processes(id),
    line_id                 BIGINT REFERENCES lines(id),
    incident_type           TEXT NOT NULL,
    severity                TEXT NOT NULL,
    description             TEXT NOT NULL,
    downtime_minutes        NUMERIC(6,2),
    production_loss_ton     NUMERIC(14,3),
    reported_by_user_id     BIGINT NOT NULL REFERENCES users(id),
    resolved_by_user_id     BIGINT REFERENCES users(id),
    created_at              TIMESTAMPTZ NOT NULL,
    resolved_at             TIMESTAMPTZ,
    resolution             TEXT
);

CREATE TABLE preventive_maintenance_tasks (
    id                      BIGSERIAL PRIMARY KEY,
    task_code               TEXT NOT NULL UNIQUE,
    equipment_type          TEXT NOT NULL,
    equipment_id            BIGINT REFERENCES belts(id),
    task_description        TEXT NOT NULL,
    frequency_days          INTEGER NOT NULL,
    last_performed_at       TIMESTAMPTZ,
    next_due_at             TIMESTAMPTZ NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Reporting y analytics
-- =========================

CREATE TABLE daily_reports (
    id                      BIGSERIAL PRIMARY KEY,
    report_date             TIMESTAMPTZ NOT NULL,
    shift_id                BIGINT REFERENCES shifts(id),
    line_id                 BIGINT REFERENCES lines(id),
    total_input_ton         NUMERIC(14,3) NOT NULL DEFAULT 0,
    total_product_a_ton     NUMERIC(14,3) NOT NULL DEFAULT 0,
    total_product_b_ton     NUMERIC(14,3) NOT NULL DEFAULT 0,
    total_discard_ton       NUMERIC(14,3) NOT NULL DEFAULT 0,
    avg_feed_rate_tph       NUMERIC(7,2),
    total_production_hours NUMERIC(6,2) NOT NULL DEFAULT 0,
    downtime_minutes        NUMERIC(6,2) NOT NULL DEFAULT 0,
    alarm_count             INTEGER NOT NULL DEFAULT 0,
    quality_samples_count   INTEGER NOT NULL DEFAULT 0,
    notes                   TEXT,
    generated_at            TIMESTAMPTZ NOT NULL
);

CREATE TABLE oee_snapshots (
    id                      BIGSERIAL PRIMARY KEY,
    line_id                 BIGINT NOT NULL REFERENCES lines(id),
    snapshot_period_start   TIMESTAMPTZ NOT NULL,
    snapshot_period_end     TIMESTAMPTZ NOT NULL,
    availability_pct       NUMERIC(5,2) NOT NULL,
    performance_pct        NUMERIC(5,2) NOT NULL,
    quality_pct            NUMERIC(5,2) NOT NULL,
    oee_pct                NUMERIC(5,2) NOT NULL,
    planned_production_minutes NUMERIC(6,2) NOT NULL,
    actual_production_minutes NUMERIC(6,2) NOT NULL,
    ideal_cycle_time_minutes NUMERIC(6,2) NOT NULL,
    total_output_ton        NUMERIC(14,3) NOT NULL,
    good_output_ton         NUMERIC(14,3) NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE energy_readings (
    id                      BIGSERIAL PRIMARY KEY,
    line_id                 BIGINT REFERENCES lines(id),
    meter_id                TEXT NOT NULL,
    reading_type            TEXT NOT NULL,
    kwh_value               NUMERIC(12,2) NOT NULL,
    power_kw                NUMERIC(8,2),
    read_at                 TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- Índices
-- =========================

CREATE INDEX idx_user_sessions_user_login ON user_sessions(user_id, login_at DESC);
CREATE INDEX idx_processes_line_status ON processes(line_id, status);
CREATE INDEX idx_processes_started_at ON processes(started_at);
CREATE INDEX idx_process_inputs_process_id ON process_inputs(process_id);
CREATE INDEX idx_process_outputs_process_id ON process_outputs(process_id);
CREATE INDEX idx_process_scale_readings_process_scale ON process_scale_readings(process_id, scale_id);
CREATE INDEX idx_scale_totalizer_history_scale_time ON scale_totalizer_history(scale_id, reading_at DESC);
CREATE INDEX idx_quarry_stock_movements_quarry_time ON quarry_stock_movements(quarry_id, created_at DESC);
CREATE INDEX idx_process_events_process_time ON process_events(process_id, created_at DESC);
CREATE INDEX idx_alarms_line_started_at ON alarms(line_id, started_at DESC);
CREATE INDEX idx_plc_variable_history_var_time ON plc_variable_history(plc_variable_id, captured_at DESC);
CREATE INDEX idx_yield_snapshots_quarry_time ON quarry_yield_snapshots(quarry_id, calculated_at DESC);
CREATE INDEX idx_quality_records_process ON quality_records(process_id);
CREATE INDEX idx_quality_records_status ON quality_records(result_status);
CREATE INDEX idx_lot_traceability_process ON lot_traceability(process_id);
CREATE INDEX idx_maintenance_requests_status ON maintenance_requests(status);
CREATE INDEX idx_maintenance_requests_priority ON maintenance_requests(priority);
CREATE INDEX idx_maintenance_incidents_line ON maintenance_incidents(line_id);
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
CREATE INDEX idx_oee_snapshots_line ON oee_snapshots(line_id);
CREATE INDEX idx_energy_readings_line ON energy_readings(line_id);

COMMIT;
