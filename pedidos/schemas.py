from pydantic import BaseModel, Field, validator
from typing import Literal


# Base opcional si quieres reutilizar atributos comunes
class PedidoBase(BaseModel):
    producto_id: int = Field(
        ..., gt=0, description="ID del producto debe ser mayor a 0"
    )
    cantidad: int = Field(..., gt=0, description="Cantidad debe ser mayor a 0")
    estado: Literal["pendiente", "pagado", "cancelado"] = Field(
        default="pendiente", description="Estado del pedido"
    )


# Para la creación de pedidos desde el cliente (total se calcula automáticamente)
class PedidoCreate(PedidoBase):
    @validator("cantidad")
    def cantidad_mayor_cero(cls, v):
        if v <= 0:
            raise ValueError("Cantidad debe ser mayor a 0")
        return v


# Para la respuesta de la API, incluye el total
class PedidoOut(PedidoBase):
    id: int
    total: float = Field(..., ge=0, description="Monto total del pedido")

    class Config:
        orm_mode = True
