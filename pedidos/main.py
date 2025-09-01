# pedidos/main.py
from fastapi import FastAPI
from . import models, db, routes

app = FastAPI(title="Microservicio de Pedidos")

# Crear tablas
models.Base.metadata.create_all(bind=db.engine)

# Incluir rutas
app.include_router(routes.router)


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Pedidos activo"}
