from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.catalog import Role, User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='Credenciales inválidas')
    if not verify_password(payload.password, user.password_hash):
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
    return TokenResponse(access_token=token, username=user.username, full_name=user.full_name, role=role)
