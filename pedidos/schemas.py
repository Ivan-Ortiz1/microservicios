from pydantic import BaseModel


# Base opcional si quieres reutilizar atributos comunes
class PedidoBase(BaseModel):
    producto_id: int
    cantidad: int
    estado: str = "pendiente"


# Para la creación de pedidos desde el cliente (total se calcula automáticamente)
class PedidoCreate(PedidoBase):
    pass


# Para la respuesta de la API, incluye el total
class PedidoOut(PedidoBase):
    id: int
    total: float

    class Config:
        orm_mode = True
