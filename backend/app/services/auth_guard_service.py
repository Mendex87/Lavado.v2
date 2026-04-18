from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.auth_security import AuthThrottle


class AuthGuardService:
    WINDOW_MINUTES = 15
    BLOCK_MINUTES = 15
    MAX_FAILS = 5

    def __init__(self, db: Session):
        self.db = db

    def check_allowed(self, username: str, ip: str) -> tuple[bool, int | None]:
        now = datetime.utcnow()
        wait_seconds = None
        for scope, key in [('user', username.lower()), ('ip', ip)]:
            row = self._get_or_create(scope, key)
            if row.blocked_until and row.blocked_until > now:
                remaining = int((row.blocked_until - now).total_seconds())
                wait_seconds = max(wait_seconds or 0, remaining)
        return (wait_seconds is None), wait_seconds

    def register_success(self, username: str, ip: str) -> None:
        for scope, key in [('user', username.lower()), ('ip', ip)]:
            row = self._get_or_create(scope, key)
            row.fail_count = 0
            row.blocked_until = None
            row.window_started_at = datetime.utcnow()
        self.db.flush()

    def register_failure(self, username: str, ip: str) -> tuple[bool, int | None]:
        now = datetime.utcnow()
        blocked = False
        wait_seconds = None

        for scope, key in [('user', username.lower()), ('ip', ip)]:
            row = self._get_or_create(scope, key)
            if not row.window_started_at or row.window_started_at < now - timedelta(minutes=self.WINDOW_MINUTES):
                row.window_started_at = now
                row.fail_count = 0
                row.blocked_until = None

            row.fail_count += 1
            if row.fail_count >= self.MAX_FAILS:
                row.blocked_until = now + timedelta(minutes=self.BLOCK_MINUTES)
                blocked = True
                wait_seconds = max(wait_seconds or 0, int((row.blocked_until - now).total_seconds()))

        self.db.flush()
        return blocked, wait_seconds

    def _get_or_create(self, scope: str, key: str) -> AuthThrottle:
        row = self.db.query(AuthThrottle).filter(AuthThrottle.scope == scope, AuthThrottle.key == key).first()
        if row:
            return row
        row = AuthThrottle(scope=scope, key=key, fail_count=0)
        self.db.add(row)
        self.db.flush()
        return row
