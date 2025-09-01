# productos/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, db, auth

router = APIRouter()


@router.post("/productos", response_model=schemas.ProductoOut)
def crear_producto(
    producto: schemas.ProductoCreate,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    nuevo = models.Producto(**producto.dict())
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


@router.get("/productos", response_model=list[schemas.ProductoOut])
def listar_productos(
    token: dict = Depends(auth.verificar_token), session: Session = Depends(db.get_db)
):
    return session.query(models.Producto).all()


@router.get("/productos/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(
    producto_id: int,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    producto = (
        session.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.put("/productos/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: schemas.ProductoCreate,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    producto = (
        session.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in datos.dict().items():
        setattr(producto, key, value)
    session.commit()
    session.refresh(producto)
    return producto


@router.delete("/productos/{producto_id}")
def eliminar_producto(
    producto_id: int,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    producto = (
        session.query(models.Producto).filter(models.Producto.id == producto_id).first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    session.delete(producto)
    session.commit()
    return {"mensaje": "Producto eliminado"}
