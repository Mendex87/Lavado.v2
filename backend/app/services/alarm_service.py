from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.events import Alarm
from app.repositories.process_repository import ProcessRepository
from app.services.measurement_service import MeasurementService
from app.schemas.alarm import AlarmItem


class AlarmService:
    STALE_SECONDS = 15
    HIGH_TPH_THRESHOLD = 200.0

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self) -> None:
        now = datetime.utcnow()
        processes = ProcessRepository(self.db).list_active()
        active_by_line = {int(p.line_id): p for p in processes}
        latest = MeasurementService(self.db).list_latest()

        by_line = {1: [], 2: []}
        for m in latest:
            by_line.setdefault(int(m.line), []).append(m)

        for line in (1, 2):
            process = active_by_line.get(line)
            if not process:
                self._close_open(line_id=line, alarm_type='PLC_STALE')
                self._close_open(line_id=line, alarm_type='FLOW_HIGH')
                continue

            captured = [m.captured_at for m in by_line.get(line, []) if m.captured_at is not None]
            last_ts = max(captured) if captured else None
            stale = True
            if last_ts:
                ts = self._to_naive_utc(last_ts)
                stale = (now - ts).total_seconds() > self.STALE_SECONDS

            if stale:
                self._open_if_missing(
                    line_id=line,
                    process_id=process.id,
                    alarm_type='PLC_STALE',
                    severity='high',
                    message=f'Línea {line}: sin lectura PLC reciente',
                    started_at=now,
                )
            else:
                self._close_open(line_id=line, alarm_type='PLC_STALE')

            tph = self._line_tph(line, by_line.get(line, []))
            if tph is not None and tph > self.HIGH_TPH_THRESHOLD:
                self._open_if_missing(
                    line_id=line,
                    process_id=process.id,
                    alarm_type='FLOW_HIGH',
                    severity='medium',
                    message=f'Línea {line}: caudal alto ({tph:.1f} tn/h)',
                    started_at=now,
                )
            else:
                self._close_open(line_id=line, alarm_type='FLOW_HIGH')

        self.db.commit()

    def list_active(self) -> list[AlarmItem]:
        self.evaluate()
        rows = (
            self.db.query(Alarm)
            .filter(Alarm.ended_at.is_(None))
            .order_by(Alarm.started_at.desc())
            .all()
        )
        return [
            AlarmItem(
                id=a.id,
                line=a.line_id,
                alarm_type=a.alarm_type,
                severity=a.severity,
                message=a.message,
                started_at=a.started_at,
                acknowledged=bool(a.acknowledged_at),
                acknowledged_at=a.acknowledged_at,
                acknowledged_by_user_id=a.acknowledged_by_user_id,
            )
            for a in rows
        ]

    def acknowledge(self, alarm_id: int, user_id: int) -> None:
        alarm = self.db.query(Alarm).filter(Alarm.id == alarm_id, Alarm.ended_at.is_(None)).first()
        if not alarm:
            raise LookupError('Alarma no encontrada')
        alarm.acknowledged_by_user_id = user_id
        alarm.acknowledged_at = datetime.utcnow()
        self.db.commit()

    def _line_tph(self, line: int, items: list) -> float | None:
        def last_partial(code: str) -> float | None:
            vals = [m.partial_ton for m in items if m.code == code and m.partial_ton is not None]
            return float(vals[-1]) if vals else None

        if line == 1:
            return last_partial('l1_input_tph')

        a = last_partial('l2_input_tph_a')
        b = last_partial('l2_input_tph_b')
        if a is not None or b is not None:
            return float(a or 0) + float(b or 0)
        return last_partial('l2_input_tph')

    def _open_if_missing(self, line_id: int, process_id: int | None, alarm_type: str, severity: str, message: str, started_at: datetime) -> None:
        exists = (
            self.db.query(Alarm)
            .filter(Alarm.line_id == line_id, Alarm.alarm_type == alarm_type, Alarm.ended_at.is_(None))
            .first()
        )
        if exists:
            return
        self.db.add(Alarm(
            process_id=process_id,
            line_id=line_id,
            alarm_type=alarm_type,
            severity=severity,
            message=message,
            started_at=started_at,
            ended_at=None,
            acknowledged_by_user_id=None,
            acknowledged_at=None,
        ))
        self.db.flush()

    def _close_open(self, line_id: int, alarm_type: str) -> None:
        row = (
            self.db.query(Alarm)
            .filter(Alarm.line_id == line_id, Alarm.alarm_type == alarm_type, Alarm.ended_at.is_(None))
            .first()
        )
        if row:
            row.ended_at = datetime.utcnow()

    def _to_naive_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
