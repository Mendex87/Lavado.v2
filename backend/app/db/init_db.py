from app.db.session import Base, SessionLocal, engine
from app import models  # noqa: F401
from app.services.seed_service import SeedService


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        SeedService(db).run()
    finally:
        db.close()


if __name__ == '__main__':
    init_db()
