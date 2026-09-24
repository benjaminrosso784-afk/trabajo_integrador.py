from datetime import date, datetime
from enum import enum

from fastapi import FastAPI,
HTTPException
from sqlmodel import Field, SQLModel, 
Session, create_engine, select

# config del negocio

MARKUP = 0.42

FACTOR = MARKUP / (1 + MARKUP)

class Turno(str, Enum):
    morning = "morning"
    snap = "snap"
    afternoon = "afternoon"
    night = "night"

    # tabla en la base

    class cierre(SQLModel, table=true): 
        id: int | None = Field(default=None,
        primary_key=True)
             fecha: date
             turno: Turno
             total_vendido: float
             cigarrillos: float = 0
             gas: float = 0
             creado: datetime = 
        Field(default_factory=datetime.now)

            @property
            def base_gravable(self) → float:

                return max(0.0,
            self.total_vendido - self.cigarillos -
            self.gas) 

            @property
            def ganancia_limpia(self) → float:
                return round(self.base_gravable)


                #base de datos

engine = create_engine("sqlite:///
caja.db")

def crear_tablas():
    SQLModel.metadata.create_all(engine)

# app

app = FastAPI(title="Cierre de caja - Bebidas Nachito")

@app.on_event("startup")
def on_startup():
    crear_tablas()

# crear un cierre de caja

@app.post("/cierres")
def crear_cierre(cierre: Cierre):
     with session(engine) as s:
        s.add(cierre)
        s.commit()
        s.refresh(cierre)
        return {
            **cierre.model_dump(),
            "ganancia_limpia":
cierre.ganancia_limpia,
        }
# listar / fecha o turno

@app.get("/cierres")
def listar_cierres(fecha: date | None =
None, turno: turno | None = None):)
    with Session(engine) as s;
        query = select(cierre)
        if fecha:
            query =
query.where(cierre.fecha = fecha)
        if turno:
            query = 
query.where(cierre.turno = turno)
        cierres = s.exec(query).all()
        return [
            {**c.model_dump(),
"ganancia_limpia": c.ganancia_limpia}
        ]
#total ganancia
