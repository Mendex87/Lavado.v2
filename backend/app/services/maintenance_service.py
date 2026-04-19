from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceRequest, MaintenanceIncident, PreventiveMaintenanceTask


class MaintenanceService:
    @staticmethod
    def generate_request_code(db: Session) -> str:
        count = db.query(func.count(MaintenanceRequest.id)).scalar() or 0
        return f"MR-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:04d}"

    @staticmethod
    def create_request(db: Session, data: dict, user_id: int) -> MaintenanceRequest:
        request = MaintenanceRequest(
            request_code=MaintenanceService.generate_request_code(db),
            request_type=data['request_type'],
            priority=data['priority'],
            line_id=data.get('line_id'),
            belt_id=data.get('belt_id'),
            scale_id=data.get('scale_id'),
            description=data['description'],
            reported_by_user_id=user_id,
            assigned_to_user_id=data.get('assigned_to_user_id'),
            created_at=datetime.utcnow(),
            status='open',
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def update_request(db: Session, request_id: int, data: dict) -> Optional[MaintenanceRequest]:
        request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not request:
            return None
        for key, value in data.items():
            if value is not None and hasattr(request, key):
                setattr(request, key, value)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_requests(db: Session, status: Optional[str] = None, priority: Optional[str] = None, limit: int = 50):
        query = db.query(MaintenanceRequest)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if priority:
            query = query.filter(MaintenanceRequest.priority == priority)
        return query.order_by(MaintenanceRequest.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_request_by_id(db: Session, request_id: int) -> Optional[MaintenanceRequest]:
        return db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()

    @staticmethod
    def acknowledge_request(db: Session, request_id: int) -> Optional[MaintenanceRequest]:
        request = MaintenanceService.get_request_by_id(db, request_id)
        if not request:
            return None
        request.status = 'acknowledged'
        request.acknowledged_at = datetime.utcnow()
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def start_work(db: Session, request_id: int) -> Optional[MaintenanceRequest]:
        request = MaintenanceService.get_request_by_id(db, request_id)
        if not request:
            return None
        request.status = 'in_progress'
        request.in_progress_at = datetime.utcnow()
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def complete_request(db: Session, request_id: int, resolution_notes: Optional[str] = None) -> Optional[MaintenanceRequest]:
        request = MaintenanceService.get_request_by_id(db, request_id)
        if not request:
            return None
        request.status = 'completed'
        request.completed_at = datetime.utcnow()
        if resolution_notes:
            request.resolution_notes = resolution_notes
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_stats(db: Session) -> dict:
        open_count = db.query(func.count(MaintenanceRequest.id)).filter(MaintenanceRequest.status == 'open').scalar() or 0
        in_progress_count = db.query(func.count(MaintenanceRequest.id)).filter(MaintenanceRequest.status == 'in_progress').scalar() or 0
        
        today = datetime.utcnow().date()
        completed_today = db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.status == 'completed',
            func.date(MaintenanceRequest.completed_at) == today
        ).scalar() or 0

        week_ago = datetime.utcnow() - timedelta(days=7)
        incidents_week = db.query(func.count(MaintenanceIncident.id)).filter(
            MaintenanceIncident.created_at >= week_ago
        ).scalar() or 0

        return {
            'open_requests': open_count,
            'in_progress': in_progress_count,
            'completed_today': completed_today,
            'incidents_this_week': incidents_week,
            'avg_resolution_time_hours': None
        }

    @staticmethod
    def generate_incident_code(db: Session) -> str:
        count = db.query(func.count(MaintenanceIncident.id)).scalar() or 0
        return f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:04d}"

    @staticmethod
    def create_incident(db: Session, data: dict, user_id: int) -> MaintenanceIncident:
        incident = MaintenanceIncident(
            incident_code=MaintenanceService.generate_incident_code(db),
            maintenance_request_id=data.get('maintenance_request_id'),
            process_id=data.get('process_id'),
            line_id=data.get('line_id'),
            incident_type=data['incident_type'],
            severity=data['severity'],
            description=data['description'],
            downtime_minutes=data.get('downtime_minutes'),
            production_loss_ton=data.get('production_loss_ton'),
            reported_by_user_id=user_id,
            created_at=datetime.utcnow(),
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def resolve_incident(db: Session, incident_id: int, user_id: int, resolution: str) -> Optional[MaintenanceIncident]:
        incident = db.query(MaintenanceIncident).filter(MaintenanceIncident.id == incident_id).first()
        if not incident:
            return None
        incident.resolved_by_user_id = user_id
        incident.resolved_at = datetime.utcnow()
        incident.resolution = resolution
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_incidents(db: Session, line_id: Optional[int] = None, limit: int = 50):
        query = db.query(MaintenanceIncident)
        if line_id:
            query = query.filter(MaintenanceIncident.line_id == line_id)
        return query.order_by(MaintenanceIncident.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_preventive_task(db: Session, data: dict) -> PreventiveMaintenanceTask:
        next_due = datetime.utcnow() + timedelta(days=data['frequency_days'])
        task = PreventiveMaintenanceTask(
            task_code=f"PM-{data['equipment_type']}-{datetime.utcnow().strftime('%Y%m%d')}",
            equipment_type=data['equipment_type'],
            equipment_id=data.get('equipment_id'),
            task_description=data['task_description'],
            frequency_days=data['frequency_days'],
            next_due_at=next_due,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_preventive_tasks(db: Session, overdue_only: bool = False):
        query = db.query(PreventiveMaintenanceTask).filter(PreventiveMaintenanceTask.is_active == True)
        if overdue_only:
            query = query.filter(PreventiveMaintenanceTask.next_due_at <= datetime.utcnow())
        return query.order_by(PreventiveMaintenanceTask.next_due_at).all()

    @staticmethod
    def complete_preventive_task(db: Session, task_id: int) -> Optional[PreventiveMaintenanceTask]:
        task = db.query(PreventiveMaintenanceTask).filter(PreventiveMaintenanceTask.id == task_id).first()
        if not task:
            return None
        task.last_performed_at = datetime.utcnow()
        task.next_due_at = datetime.utcnow() + timedelta(days=task.frequency_days)
        db.commit()
        db.refresh(task)
        return task