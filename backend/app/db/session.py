from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings

settings = get_settings()
is_sqlite = settings.sqlalchemy_database_uri.startswith('sqlite')
connect_args = {'check_same_thread': False, 'timeout': 15} if is_sqlite else {}
engine = create_engine(settings.sqlalchemy_database_uri, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

if is_sqlite:
    @event.listens_for(engine, 'connect')
    def _set_sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute('PRAGMA synchronous=NORMAL;')
        cursor.execute('PRAGMA busy_timeout=15000;')
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_measurement_readings_point_id_id ON measurement_readings(measurement_point_id, id DESC);')
        except Exception:
            pass
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quarry_stock_movements_quarry_id_id ON quarry_stock_movements(quarry_id, id DESC);')
        except Exception:
            pass
        cursor.close()


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
