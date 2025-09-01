from pydantic import BaseModel, Field


# 🔹 Base con validaciones
class PagoBase(BaseModel):
    pedido_id: int = Field(..., gt=0, description="ID del pedido asociado")
    monto: float = Field(..., gt=0, description="Monto a pagar")
    estado: str = Field(default="aprobado", description="Estado del pago")


# 🔹 Para creación de pagos (lo que recibe el microservicio de pagos)
class PagoCreate(PagoBase):
    pass


# 🔹 Para respuestas de la API (incluye ID)
class PagoOut(PagoBase):
    id: int

    class Config:
        orm_mode = True
