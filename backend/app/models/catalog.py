from sqlalchemy import Boolean, ForeignKey, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModelORM


class Role(BaseModelORM):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class User(BaseModelORM):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserRole(BaseModelORM):
    __tablename__ = 'user_roles'
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)


class Shift(BaseModelORM):
    __tablename__ = 'shifts'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[object] = mapped_column(Time, nullable=False)
    end_time: Mapped[object] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserSession(BaseModelORM):
    __tablename__ = 'user_sessions'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    shift_id: Mapped[int | None] = mapped_column(ForeignKey('shifts.id'))
    auth_source: Mapped[str] = mapped_column(String, nullable=False, default='app')
    device_label: Mapped[str | None] = mapped_column(String)
    app_version: Mapped[str | None] = mapped_column(String)


class Line(BaseModelORM):
    __tablename__ = 'lines'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Quarry(BaseModelORM):
    __tablename__ = 'quarries'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Product(BaseModelORM):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    mesh_label: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class QuarryProduct(BaseModelORM):
    __tablename__ = 'quarry_products'
    __table_args__ = (UniqueConstraint('quarry_id', 'product_id', name='uq_quarry_product'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarries.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Belt(BaseModelORM):
    __tablename__ = 'belts'
    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    purpose: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Scale(BaseModelORM):
    __tablename__ = 'scales'
    id: Mapped[int] = mapped_column(primary_key=True)
    belt_id: Mapped[int | None] = mapped_column(ForeignKey('belts.id'))
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    scale_kind: Mapped[str] = mapped_column(String, nullable=False)
    plc_tag_prefix: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
