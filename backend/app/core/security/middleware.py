from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
from jose import jwt, JWTError

from app.core.security.auth import (
    _require_secret_key,
    ALGORITHM,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
)

class SlidingSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        token = request.cookies.get("access_token")
        if token:
            try:
                # Backward compatibility: older cookies may store "Bearer <token>"
                if token.lower().startswith("bearer "):
                    token = token.split(" ", 1)[1].strip()

                # Decode token to get expiration date
                payload = jwt.decode(token, _require_secret_key(), algorithms=[ALGORITHM])
                exp = payload.get("exp")
                
                if exp:
                    # JWT uses UTC timestamps
                    exp_time = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)
                    now = datetime.utcnow()
                    remaining_seconds = (exp_time - now).total_seconds()
                    remaining_minutes = remaining_seconds / 60
                    
                    # If remaining time is less than half of the total expiration time, refresh it
                    if 0 < remaining_minutes < (ACCESS_TOKEN_EXPIRE_MINUTES / 2):
                        new_token = create_access_token({"sub": payload.get("sub")})
                        max_age_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
                        response.set_cookie(
                            key="access_token",
                            value=new_token,
                            httponly=True,
                            max_age=max_age_seconds,
                            expires=max_age_seconds,
                            samesite=COOKIE_SAMESITE,
                            secure=COOKIE_SECURE
                        )
            except JWTError:
                # Invalid or expired token, let normal auth flow (get_current_user) handle it
                pass

        return response
