# productos/auth.py
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Depends, Header

SECRET_KEY = "supersecreto"
ALGORITHM = "HS256"


def crear_token(data: dict, expira_en: Optional[int] = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expira_en)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Token inválido")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado")
