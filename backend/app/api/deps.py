from collections.abc import Callable
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.catalog import Role, User, UserRole
from app.core.security import decode_access_token


def db_session() -> Session:
    return next(get_db())


bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        username = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail='Usuario inválido')
    return user


def get_current_user_roles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> set[str]:
    rows = (
        db.query(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    return {str(code) for (code,) in rows}


def require_roles(*allowed: str) -> Callable:
    allowed_set = {r.strip().lower() for r in allowed if r.strip()}

    def _dep(roles: set[str] = Depends(get_current_user_roles)) -> None:
        normalized = {r.lower() for r in roles}
        if not normalized.intersection(allowed_set):
            raise HTTPException(status_code=403, detail='Permisos insuficientes')

    return _dep
