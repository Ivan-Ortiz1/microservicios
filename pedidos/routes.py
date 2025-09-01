from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, db, auth
import httpx

PRODUCTOS_URL = "http://127.0.0.1:8000"
PAGOS_URL = "http://127.0.0.1:8002"

router = APIRouter()


@router.post("/pedidos", response_model=schemas.PedidoOut)
def crear_pedido(
    pedido: schemas.PedidoCreate,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):

    # 1. Verificar stock
    with httpx.Client() as client:
        resp = client.get(
            f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
            headers={"Authorization": f"Bearer {auth.crear_token({'sub':'admin'})}"},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Producto no encontrado")

        producto = resp.json()
        if producto["stock"] < pedido.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")

        # 2. Descontar stock
        nuevo_stock = producto["stock"] - pedido.cantidad
        client.put(
            f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
            json={
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "stock": nuevo_stock,
                "descripcion": producto.get("descripcion", ""),
            },
            headers={"Authorization": f"Bearer {auth.crear_token({'sub':'admin'})}"},
        )

    # 3. Crear el pedido en la DB local con total calculado
    total = producto["precio"] * pedido.cantidad
    nuevo_pedido = models.Pedido(
        producto_id=pedido.producto_id,
        cantidad=pedido.cantidad,
        total=total,
        estado="pendiente",
    )
    session.add(nuevo_pedido)
    session.commit()
    session.refresh(nuevo_pedido)

    # 4. Registrar el pago
    with httpx.Client() as client:
        pago_resp = client.post(
            f"{PAGOS_URL}/pagos",
            json={
                "pedido_id": nuevo_pedido.id,
                "monto": total,
            },
            headers={"Authorization": f"Bearer {auth.crear_token({'sub':'admin'})}"},
        )
        if pago_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al procesar el pago")

    return nuevo_pedido
