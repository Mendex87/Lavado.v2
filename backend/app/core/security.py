from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import get_settings

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def is_password_hash(value: str) -> bool:
    return value.startswith('$')


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    to_encode = {'sub': subject, 'exp': expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm='HS256')


def decode_access_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=['HS256'])
    except JWTError as exc:
        raise ValueError('Token inválido') from exc
    sub = payload.get('sub')
    if not sub:
        raise ValueError('Token sin subject')
    return str(sub)
