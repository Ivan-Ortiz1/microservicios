from pydantic import BaseModel, Field
from typing import Literal


# 🔹 Base con validaciones y estado limitado
class PagoBase(BaseModel):
    pedido_id: int = Field(..., gt=0, description="ID del pedido asociado")
    monto: float = Field(..., gt=0, description="Monto a pagar")
    estado: Literal["aprobado", "rechazado"] = Field(
        default="aprobado", description="Estado del pago"
    )


# 🔹 Para creación de pagos (lo que recibe el microservicio de pagos)
class PagoCreate(PagoBase):
    pass


# 🔹 Para respuestas de la API (incluye ID y validaciones)
class PagoOut(PagoBase):
    id: int

    class Config:
        orm_mode = True
