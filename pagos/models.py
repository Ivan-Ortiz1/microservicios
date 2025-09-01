# pagos/models.py
from sqlalchemy import Column, Integer, Float, String
from .db import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer)
    monto = Column(Float)
    estado = Column(String, default="aprobado")  # siempre aprobado para simplificar
