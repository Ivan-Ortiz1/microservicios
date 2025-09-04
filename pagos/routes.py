# pagos/routes.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)  # Nos permite separar las rutas (endpoints) y Depends: Es una herramienta de FastAPI que inyecta dependencias
from sqlalchemy.orm import (
    Session,
)  # Objeto de SQLAlchemy que representa una conexión activa a la base de datos.
from . import (
    models,
    schemas,
    db,
    auth,
)  # Nuestros módulos donde definimos modelos de DB, validaciones Pydantic, conexión a DB y autenticación.

router = APIRouter()


@router.post("/pagos", response_model=schemas.PagoOut)
def procesar_pago(
    pago: schemas.PagoCreate,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    nuevo_pago = models.Pago(**pago.dict())
    session.add(nuevo_pago)
    session.commit()
    session.refresh(nuevo_pago)
    return nuevo_pago


@router.get("/pagos", response_model=list[schemas.PagoOut])
def listar_pagos(
    token: dict = Depends(auth.verificar_token), session: Session = Depends(db.get_db)
):
    return session.query(models.Pago).all()
