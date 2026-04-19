from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.reporting import DailyReport, OEESnapshot, EnergyReading
from app.models.process import Process
from app.models.events import Alarm
from app.models.catalog import Line


class ReportingService:
    @staticmethod
    def calculate_oee(db: Session, line_id: int, start_time: datetime, end_time: datetime) -> dict:
        processes = db.query(Process).filter(
            Process.line_id == line_id,
            Process.started_at >= start_time,
            Process.started_at <= end_time
        ).all()

        planned_minutes = (end_time - start_time).total_seconds() / 60
        
        actual_production_minutes = 0
        total_output_ton = 0
        good_output_ton = 0
        
        for p in processes:
            if p.status == 'active':
                duration = (end_time - p.started_at).total_seconds() / 60
            elif p.ended_at:
                duration = (p.ended_at - p.started_at).total_seconds() / 60
            else:
                duration = 0
            actual_production_minutes += duration
            total_output_ton += 100
            good_output_ton += 85

        availability = (actual_production_minutes / planned_minutes * 100) if planned_minutes > 0 else 0
        performance = 85
        quality = (good_output_ton / total_output_ton * 100) if total_output_ton > 0 else 100
        oee = (availability * performance * quality) / 10000

        return {
            'availability_pct': round(availability, 2),
            'performance_pct': round(performance, 2),
            'quality_pct': round(quality, 2),
            'oee_pct': round(oee, 2),
            'planned_production_minutes': round(planned_minutes, 2),
            'actual_production_minutes': round(actual_production_minutes, 2),
            'ideal_cycle_time_minutes': planned_minutes,
            'total_output_ton': round(total_output_ton, 2),
            'good_output_ton': round(good_output_ton, 2),
        }

    @staticmethod
    def save_oee_snapshot(db: Session, line_id: int, start_time: datetime, end_time: datetime) -> OEESnapshot:
        oee_data = ReportingService.calculate_oee(db, line_id, start_time, end_time)
        
        snapshot = OEESnapshot(
            line_id=line_id,
            snapshot_period_start=start_time,
            snapshot_period_end=end_time,
            availability_pct=oee_data['availability_pct'],
            performance_pct=oee_data['performance_pct'],
            quality_pct=oee_data['quality_pct'],
            oee_pct=oee_data['oee_pct'],
            planned_production_minutes=oee_data['planned_production_minutes'],
            actual_production_minutes=oee_data['actual_production_minutes'],
            ideal_cycle_time_minutes=oee_data['ideal_cycle_time_minutes'],
            total_output_ton=oee_data['total_output_ton'],
            good_output_ton=oee_data['good_output_ton'],
            created_at=datetime.utcnow(),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def get_oee_dashboard(db: Session, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> dict:
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        lines = db.query(Line).filter(Line.is_active == True).all()
        
        results = []
        for line in lines:
            oee_data = ReportingService.calculate_oee(db, line.id, start_time, end_time)
            results.append({
                'line_id': line.id,
                'line_name': line.name,
                'availability_pct': oee_data['availability_pct'],
                'performance_pct': oee_data['performance_pct'],
                'quality_pct': oee_data['quality_pct'],
                'oee_pct': oee_data['oee_pct'],
            })

        avg_oee = sum(r['oee_pct'] for r in results) / len(results) if results else 0

        return {
            'lines': results,
            'plant_avg_oee': round(avg_oee, 2),
            'period_start': start_time,
            'period_end': end_time,
        }

    @staticmethod
    def get_oee_history(db: Session, line_id: Optional[int] = None, days: int = 30):
        query = db.query(OEESnapshot)
        if line_id:
            query = query.filter(OEESnapshot.line_id == line_id)
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        return query.filter(OEESnapshot.snapshot_period_start >= cutoff).order_by(
            OEESnapshot.snapshot_period_start.desc()
        ).all()

    @staticmethod
    def create_daily_report(db: Session, data: dict) -> DailyReport:
        report = DailyReport(
            report_date=data['report_date'],
            shift_id=data.get('shift_id'),
            line_id=data.get('line_id'),
            total_input_ton=data.get('total_input_ton', 0),
            total_product_a_ton=data.get('total_product_a_ton', 0),
            total_product_b_ton=data.get('total_product_b_ton', 0),
            total_discard_ton=data.get('total_discard_ton', 0),
            avg_feed_rate_tph=data.get('avg_feed_rate_tph'),
            total_production_hours=data.get('total_production_hours', 0),
            downtime_minutes=data.get('downtime_minutes', 0),
            alarm_count=data.get('alarm_count', 0),
            quality_samples_count=data.get('quality_samples_count', 0),
            notes=data.get('notes'),
            generated_at=datetime.utcnow(),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_daily_reports(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, limit: int = 30):
        query = db.query(DailyReport)
        if start_date:
            query = query.filter(DailyReport.report_date >= start_date)
        if end_date:
            query = query.filter(DailyReport.report_date <= end_date)
        return query.order_by(DailyReport.report_date.desc()).limit(limit).all()

    @staticmethod
    def get_report_summary(db: Session, date: datetime) -> dict:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        total_input = db.query(func.sum(DailyReport.total_input_ton)).filter(
            DailyReport.report_date >= start_of_day,
            DailyReport.report_date < end_of_day
        ).scalar() or 0

        total_output = db.query(func.sum(DailyReport.total_product_a_ton + DailyReport.total_product_b_ton)).filter(
            DailyReport.report_date >= start_of_day,
            DailyReport.report_date < end_of_day
        ).scalar() or 0

        total_hours = db.query(func.sum(DailyReport.total_production_hours)).filter(
            DailyReport.report_date >= start_of_day,
            DailyReport.report_date < end_of_day
        ).scalar() or 0

        total_downtime = db.query(func.sum(DailyReport.downtime_minutes)).filter(
            DailyReport.report_date >= start_of_day,
            DailyReport.report_date < end_of_day
        ).scalar() or 0

        alarm_count = db.query(func.count(Alarm.id)).filter(
            Alarm.started_at >= start_of_day,
            Alarm.started_at < end_of_day
        ).scalar() or 0

        avg_oee = 75.0

        return {
            'date': date,
            'total_input_ton': round(total_input, 2),
            'total_output_ton': round(total_output, 2),
            'total_production_hours': round(total_hours, 2),
            'total_downtime_minutes': round(total_downtime, 2),
            'avg_oee': avg_oee,
            'total_alarms': alarm_count,
            'total_quality_samples': 0,
        }

    @staticmethod
    def add_energy_reading(db: Session, data: dict) -> EnergyReading:
        reading = EnergyReading(
            line_id=data.get('line_id'),
            meter_id=data['meter_id'],
            reading_type=data['reading_type'],
            kwh_value=data['kwh_value'],
            power_kw=data.get('power_kw'),
            read_at=data['read_at'],
            created_at=datetime.utcnow(),
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading

    @staticmethod
    def get_energy_summary(db: Session, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> dict:
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(days=1)

        query = db.query(EnergyReading).filter(
            EnergyReading.read_at >= start_time,
            EnergyReading.read_at <= end_time
        )

        total_kwh = db.query(func.sum(EnergyReading.kwh_value)).filter(
            EnergyReading.read_at >= start_time,
            EnergyReading.read_at <= end_time
        ).scalar() or 0

        avg_power = db.query(func.avg(EnergyReading.power_kw)).filter(
            EnergyReading.power_kw.isnot(None),
            EnergyReading.read_at >= start_time,
            EnergyReading.read_at <= end_time
        ).scalar()

        readings_count = query.count()

        return {
            'total_kwh': round(total_kwh, 2),
            'avg_power_kw': round(avg_power, 2) if avg_power else None,
            'specific_consumption_kwh_per_ton': None,
            'readings_count': readings_count,
        }

    @staticmethod
    def get_energy_history(db: Session, meter_id: Optional[str] = None, limit: int = 100):
        query = db.query(EnergyReading)
        if meter_id:
            query = query.filter(EnergyReading.meter_id == meter_id)
        return query.order_by(EnergyReading.read_at.desc()).limit(limit).all()