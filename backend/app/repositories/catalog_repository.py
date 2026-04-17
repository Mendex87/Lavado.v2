from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.catalog import Product, Quarry, Shift, User


class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def get_default_shift(self) -> Shift | None:
        return self.db.scalar(select(Shift).order_by(Shift.id.asc()))

    def get_quarries_by_names(self, names: list[str]) -> list[Quarry]:
        if not names:
            return []
        rows = self.db.scalars(select(Quarry).where(Quarry.name.in_(names))).all()
        return list(rows)

    def get_product_by_name(self, name: str | None) -> Product | None:
        if not name:
            return None
        return self.db.scalar(select(Product).where(Product.name == name))
