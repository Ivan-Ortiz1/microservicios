# pedidos/models.py
from sqlalchemy import Column, Integer, String, Float
from .db import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer)
    cantidad = Column(Integer)
    estado = Column(String, default="pendiente")
    total = Column(Float)
