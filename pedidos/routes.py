from fastapi import APIRouter, Depends, HTTPException
from pagos.schemas import PagoCreate
from sqlalchemy.orm import Session
from . import models, schemas, db, auth
import httpx
import logging
import time

PRODUCTOS_URL = "http://127.0.0.1:8000"
PAGOS_URL = "http://127.0.0.1:8002"

router = APIRouter()
logging.basicConfig(level=logging.INFO)


class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=10):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.open = False

    def call(self, func, *args, **kwargs):
        if self.open:
            if time.time() - self.last_failure_time > self.reset_timeout:
                # Reintentar después del timeout
                self.open = False
                self.failures = 0
            else:
                raise Exception(
                    "Circuito abierto. Servicio temporalmente no disponible."
                )

        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures:
                self.open = True
            raise


# Instancias de Circuit Breaker para productos y pagos
productos_cb = CircuitBreaker(max_failures=3, reset_timeout=10)
pagos_cb = CircuitBreaker(max_failures=3, reset_timeout=10)


@router.post("/pedidos", response_model=schemas.PedidoOut)
def crear_pedido(
    pedido: schemas.PedidoCreate,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    if pedido.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    try:
        with httpx.Client(timeout=5.0) as client:
            # 1. Obtener producto con Circuit Breaker
            resp = productos_cb.call(
                client.get,
                f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
                headers={
                    "Authorization": f"Bearer {auth.crear_token({'sub': 'admin'})}"
                },
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            producto = resp.json()
            if producto["stock"] < pedido.cantidad:
                raise HTTPException(status_code=400, detail="Stock insuficiente")

            # 2. Calcular total y descontar stock
            total = producto["precio"] * pedido.cantidad
            nuevo_stock = producto["stock"] - pedido.cantidad

            stock_resp = productos_cb.call(
                client.put,
                f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
                json={
                    "nombre": producto["nombre"],
                    "precio": producto["precio"],
                    "stock": nuevo_stock,
                    "descripcion": producto.get("descripcion", ""),
                },
                headers={
                    "Authorization": f"Bearer {auth.crear_token({'sub': 'admin'})}"
                },
            )
            if stock_resp.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Error al actualizar stock del producto"
                )

            # 3. Crear pedido en DB
            nuevo_pedido = models.Pedido(
                producto_id=pedido.producto_id,
                cantidad=pedido.cantidad,
                total=total,
                estado="pendiente",
            )
            session.add(nuevo_pedido)
            session.commit()
            session.refresh(nuevo_pedido)
            logging.info(f"Pedido {nuevo_pedido.id} creado exitosamente.")

            # 4. Registrar pago con Circuit Breaker y rollback seguro
            pago_data = PagoCreate(pedido_id=nuevo_pedido.id, monto=total)
            pago_resp = pagos_cb.call(
                client.post,
                f"{PAGOS_URL}/pagos",
                json=pago_data.dict(),
                headers={
                    "Authorization": f"Bearer {auth.crear_token({'sub': 'admin'})}"
                },
            )

            if pago_resp.status_code != 200:
                logging.error(f"Error al procesar pago para pedido {nuevo_pedido.id}.")
                # Rollback: devolver stock y eliminar pedido
                productos_cb.call(
                    client.put,
                    f"{PRODUCTOS_URL}/productos/{pedido.producto_id}",
                    json={
                        "nombre": producto["nombre"],
                        "precio": producto["precio"],
                        "stock": producto["stock"],
                        "descripcion": producto.get("descripcion", ""),
                    },
                    headers={
                        "Authorization": f"Bearer {auth.crear_token({'sub': 'admin'})}"
                    },
                )
                session.delete(nuevo_pedido)
                session.commit()
                raise HTTPException(status_code=400, detail="Error al procesar el pago")

        return nuevo_pedido

    except httpx.RequestError:
        logging.error("Error de conexión con otro microservicio.")
        raise HTTPException(
            status_code=500, detail="Error de conexión con otro microservicio"
        )
    except Exception as e:
        logging.exception("Error inesperado al procesar pedido.")
        session.rollback()
        raise HTTPException(
            status_code=400, detail=f"Error procesando pedido: {str(e)}"
        )


@router.get("/pedidos", response_model=list[schemas.PedidoOut])
def listar_pedidos(
    token: dict = Depends(auth.verificar_token), session: Session = Depends(db.get_db)
):
    return session.query(models.Pedido).all()


@router.get("/pedidos/{pedido_id}", response_model=schemas.PedidoOut)
def obtener_pedido(
    pedido_id: int,
    token: dict = Depends(auth.verificar_token),
    session: Session = Depends(db.get_db),
):
    pedido = session.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido
