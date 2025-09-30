from datetime import datetime, timedelta, timezone
import jwt  # PyJWT
from core.project_config import ProjectConfig

cfg = ProjectConfig()

def create_access_token(*, sub: str, role: str, expires_minutes: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp_minutes = expires_minutes or cfg.ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "sub": sub,      # user_id
        "role": role,    # EMPLOYEE | ADMIN
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)  # HS256 por defecto :contentReference[oaicite:5]{index=5}

def decode_token(token: str) -> dict:
    # puedes exigir claims con options={"require": ["exp","sub"]} si lo deseas. :contentReference[oaicite:6]{index=6}
    return jwt.decode(token, cfg.JWT_SECRET, algorithms=[cfg.JWT_ALGORITHM])
