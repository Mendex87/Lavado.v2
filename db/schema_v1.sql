-- Proyecto planta de lavado de arena de fracking
-- Esquema base v1
-- Objetivo: núcleo sólido, relacional y escalable
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
    role_id         BIGINT NOT NULL REFERENCES roles(id),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
    -- examples: entry, final_output, configurable_output
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scales (
    id              BIGSERIAL PRIMARY KEY,
    belt_id         BIGINT REFERENCES belts(id),
    code            TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    scale_kind      TEXT NOT NULL,
    -- examples: entry, output, configurable_output
    plc_tag_prefix  TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (scale_kind IN ('entry', 'output', 'configurable_output'))
);

-- =========================
-- Procesos
-- =========================

CREATE TABLE processes (
    id                      BIGSERIAL PRIMARY KEY,
    code                    TEXT NOT NULL UNIQUE,
    line_id                 BIGINT NOT NULL REFERENCES lines(id),
    shift_id                BIGINT NOT NULL REFERENCES shifts(id),
    operator_user_id        BIGINT NOT NULL REFERENCES users(id),
    supervisor_user_id      BIGINT REFERENCES users(id),
    mode                    TEXT NOT NULL,
    status                  TEXT NOT NULL,
    started_at              TIMESTAMPTZ NOT NULL,
    ended_at                TIMESTAMPTZ,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (mode IN ('simple', 'blend')),
    CHECK (status IN ('active', 'closed', 'cancelled'))
);

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
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (classification IN ('product', 'discard')),
    CHECK (expected_humidity_pct IS NULL OR (expected_humidity_pct >= 0 AND expected_humidity_pct <= 100)),
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

CREATE TABLE process_production (
    id                      BIGSERIAL PRIMARY KEY,
    process_id              BIGINT NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    process_output_id       BIGINT REFERENCES process_outputs(id) ON DELETE SET NULL,
    scale_id                BIGINT NOT NULL REFERENCES scales(id),
    product_id              BIGINT REFERENCES products(id),
    classification          TEXT NOT NULL,
    wet_ton                 NUMERIC(14,3) NOT NULL DEFAULT 0,
    humidity_pct            NUMERIC(5,2),
    dry_ton                 NUMERIC(14,3),
    measured_at             TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (classification IN ('product', 'discard')),
    CHECK (humidity_pct IS NULL OR (humidity_pct >= 0 AND humidity_pct <= 100))
);

-- =========================
-- Stock
-- =========================

CREATE TABLE quarry_stock (
    id                      BIGSERIAL PRIMARY KEY,
    quarry_id               BIGINT NOT NULL UNIQUE REFERENCES quarries(id) ON DELETE CASCADE,
    current_ton             NUMERIC(14,3) NOT NULL DEFAULT 0,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quarry_stock_movements (
    id                      BIGSERIAL PRIMARY KEY,
    quarry_id               BIGINT NOT NULL REFERENCES quarries(id),
    process_id              BIGINT REFERENCES processes(id),
    scale_id                BIGINT REFERENCES scales(id),
    movement_type           TEXT NOT NULL,
    quantity_ton            NUMERIC(14,3) NOT NULL,
    entered_by_user_id      BIGINT NOT NULL REFERENCES users(id),
    reason                  TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (movement_type IN ('input', 'consumption', 'adjustment'))
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
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (direction IN ('plc_to_app', 'app_to_plc'))
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
-- Índices
-- =========================

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

COMMIT;
