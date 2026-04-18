from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.catalog import Role, User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import create_access_token, verify_password
from app.services.auth_guard_service import AuthGuardService
from app.services.audit_service import AuditService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    forwarded_for = request.headers.get('x-forwarded-for', '').split(',')[0].strip()
    ip = forwarded_for or (request.client.host if request.client else 'unknown')
    guard = AuthGuardService(db)
    audit = AuditService(db)

    allowed, wait_seconds = guard.check_allowed(payload.username, ip)
    if not allowed:
        audit.log(
            user_id=None,
            entity_name='auth',
            entity_id=payload.username,
            action='login_blocked',
            after_json={'ip': ip, 'wait_seconds': wait_seconds},
        )
        db.commit()
        raise HTTPException(
            status_code=429,
            detail=f'Demasiados intentos. Reintentar en {wait_seconds}s',
            headers={'Retry-After': str(wait_seconds or 0)},
        )

    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not user.is_active:
        blocked, wait_after = guard.register_failure(payload.username, ip)
        audit.log(
            user_id=None,
            entity_name='auth',
            entity_id=payload.username,
            action='login_failed',
            after_json={'ip': ip, 'blocked': blocked},
        )
        db.commit()
        if blocked:
            raise HTTPException(
                status_code=429,
                detail=f'Demasiados intentos. Reintentar en {wait_after}s',
                headers={'Retry-After': str(wait_after or 0)},
            )
        raise HTTPException(status_code=401, detail='Credenciales inválidas')
    if not verify_password(payload.password, user.password_hash):
        blocked, wait_after = guard.register_failure(payload.username, ip)
        audit.log(
            user_id=user.id,
            entity_name='auth',
            entity_id=payload.username,
            action='login_failed',
            after_json={'ip': ip, 'blocked': blocked},
        )
        db.commit()
        if blocked:
            raise HTTPException(
                status_code=429,
                detail=f'Demasiados intentos. Reintentar en {wait_after}s',
                headers={'Retry-After': str(wait_after or 0)},
            )
        raise HTTPException(status_code=401, detail='Credenciales inválidas')

    role_rows = (
        db.query(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    codes = {str(code) for (code,) in role_rows}
    if 'admin' in codes:
        role = 'admin'
    elif 'supervisor' in codes:
        role = 'supervisor'
    elif 'operador' in codes:
        role = 'operador'
    else:
        role = 'operador'

    token = create_access_token(subject=user.username)
    guard.register_success(payload.username, ip)
    audit.log(
        user_id=user.id,
        entity_name='auth',
        entity_id=user.username,
        action='login_success',
        after_json={'ip': ip, 'role': role},
    )
    db.commit()
    return TokenResponse(access_token=token, username=user.username, full_name=user.full_name, role=role)
