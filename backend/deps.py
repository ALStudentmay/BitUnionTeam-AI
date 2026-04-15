"""FastAPI-зависимости: БД и текущий пользователь."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db import get_db
from db_models import User
from security import decode_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    uid = decode_token(creds.credentials)
    if uid is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    user = db.query(User).filter(User.id == uid).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
