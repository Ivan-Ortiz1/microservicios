# pagos/schemas.py
from pydantic import BaseModel


class PagoBase(BaseModel):
    pedido_id: int
    monto: float
    estado: str = "aprobado"


class PagoCreate(PagoBase):
    pass


class PagoOut(PagoBase):
    id: int

    class Config:
        orm_mode = True
