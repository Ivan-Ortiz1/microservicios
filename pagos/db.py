# pagos/db.py
from sqlalchemy import create_engine  # Crea una conexión a la base de datos SQLite
from sqlalchemy.ext.declarative import (
    declarative_base,
)  # Clase base para definir modelos (tablas) de SQLAlchemy.
from sqlalchemy.orm import (
    sessionmaker,
)  # Crea sesiones para interactuar con la base (consultar, insertar, actualizar).

DATABASE_URL = "sqlite:///./pagos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
