from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.seed_service import SeedService

router = APIRouter(prefix='/admin', tags=['admin'])


@router.post('/seed')
def seed_data(db: Session = Depends(get_db)):
    return SeedService(db).run()
