# pagos/main.py
from fastapi import FastAPI
from . import models, db, routes

app = FastAPI(title="Microservicio de Pagos")

models.Base.metadata.create_all(bind=db.engine)

app.include_router(routes.router)


@app.get("/")
def root():
    return {"mensaje": "Microservicio de Pagos activo"}
