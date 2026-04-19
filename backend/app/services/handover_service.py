from datetime import datetime
from decimal import Decimal
from app.models.handover import HandoverRecord, HandoverChecklistItem
from app.models.catalog import Quarry
from app.models.stock import QuarryStock
from app.models.process import Process
from app.repositories.stock_repository import StockRepository
from sqlalchemy.orm import Session


class HandoverService:
    DEFAULT_CHECKLIST = [
        "Verificar stock de canteras principales",
        "Confirmar procesos activos y su estado",
        "Revisar alarmas activas sin reconocer",
        "Verificar última lectura PLC",
        "Confirmar mantenimiento pendiente",
        "Revisar producción del turno",
        "Documentar incidencias del turno",
        "Validar ingresos de stock del turno",
    ]

    def __init__(self, db: Session):
        self.db = db

    def start_handover(self, from_user_id: int, to_user_id: int, from_shift_id: int, to_shift_id: int) -> dict:
        """Inicia un handover de turno"""
        
        # Obtener resumen de procesos activos
        active_processes = self.db.query(Process).filter(Process.status == 'active').all()
        process_summary = []
        for p in active_processes:
            process_summary.append({
                'code': p.code,
                'line': p.line_id,
                'mode': p.mode,
                'started_at': p.started_at.isoformat() if p.started_at else None,
            })

        # Obtener resumen de stock
        quarries = self.db.query(Quarry).filter(Quarry.is_active == True).all()
        stock_summary = []
        for q in quarries:
            stock = self.db.query(QuarryStock).filter(QuarryStock.quarry_id == q.id).first()
            if stock:
                stock_summary.append({
                    'quarry': q.name,
                    'current_ton': float(stock.current_ton),
                    'threshold_critical': float(stock.threshold_critical),
                    'threshold_low': float(stock.threshold_low),
                })

        # Crear registro de handover
        handover = HandoverRecord(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            from_shift_id=from_shift_id,
            to_shift_id=to_shift_id,
            handover_started_at=datetime.utcnow(),
            status='pending',
            process_summary_json=process_summary,
            stock_summary_json=stock_summary,
            pending_issues_json=[],
        )
        self.db.add(handover)
        self.db.flush()

        # Crear checklist por defecto
        for item_text in self.DEFAULT_CHECKLIST:
            checklist_item = HandoverChecklistItem(
                handover_id=handover.id,
                item_text=item_text,
            )
            self.db.add(checklist_item)

        self.db.commit()

        return {
            'id': handover.id,
            'status': handover.status,
            'process_summary': process_summary,
            'stock_summary': stock_summary,
            'checklist': self.DEFAULT_CHECKLIST,
        }

    def complete_handover(self, handover_id: int, checklist_results: list, notes: str = None) -> dict:
        """Completa un handover de turno"""
        handover = self.db.query(HandoverRecord).filter(HandoverRecord.id == handover_id).first()
        if not handover:
            raise ValueError('Handover no encontrado')
        
        if handover.status != 'pending':
            raise ValueError('El handover no está en estado pending')

        # Actualizar checklist
        for item in checklist_results:
            checklist_item = self.db.query(HandoverChecklistItem).filter(
                HandoverChecklistItem.id == item['id']
            ).first()
            if checklist_item:
                checklist_item.checked = item['checked']
                if item['checked']:
                    checklist_item.checked_at = datetime.utcnow()

        # Completar handover
        handover.handover_completed_at = datetime.utcnow()
        handover.status = 'completed'
        if notes:
            handover.notes = notes

        self.db.commit()

        return {
            'id': handover.id,
            'status': 'completed',
            'completed_at': handover.handover_completed_at.isoformat(),
        }

    def get_pending_handover(self, user_id: int) -> dict | None:
        """Obtiene el handover pendiente actual para un usuario"""
        handover = self.db.query(HandoverRecord).filter(
            HandoverRecord.status == 'pending',
            HandoverRecord.to_user_id == user_id
        ).first()

        if not handover:
            return None

        # Obtener checklist
        checklist = self.db.query(HandoverChecklistItem).filter(
            HandoverChecklistItem.handover_id == handover.id
        ).all()

        return {
            'id': handover.id,
            'from_user_id': handover.from_user_id,
            'process_summary': handover.process_summary_json,
            'stock_summary': handover.stock_summary_json,
            'pending_issues': handover.pending_issues_json or [],
            'checklist': [
                {
                    'id': item.id,
                    'text': item.item_text,
                    'checked': item.checked,
                    'checked_at': item.checked_at.isoformat() if item.checked_at else None,
                }
                for item in checklist
            ],
        }

    def get_handover_history(self, user_id: int = None, limit: int = 10) -> list:
        """Obtiene el historial de handovers"""
        query = self.db.query(HandoverRecord).order_by(HandoverRecord.handover_started_at.desc())
        if user_id:
            query = query.filter(
                (HandoverRecord.from_user_id == user_id) | 
                (HandoverRecord.to_user_id == user_id)
            )
        
        handovers = query.limit(limit).all()
        
        return [
            {
                'id': h.id,
                'from_user_id': h.from_user_id,
                'to_user_id': h.to_user_id,
                'started_at': h.handover_started_at.isoformat() if h.handover_started_at else None,
                'completed_at': h.handover_completed_at.isoformat() if h.handover_completed_at else None,
                'status': h.status,
            }
            for h in handovers
        ]