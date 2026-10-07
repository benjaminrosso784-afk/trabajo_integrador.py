from datetime import date, datetime
from enum import Enum

from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Business configuration
MARKUP = 0.42
FACTOR = MARKUP / (1 + MARKUP)


class Shift(str, Enum):
    morning = "morning"
    snap = "snap"
    afternoon = "afternoon"
    night = "night"


# Database Model
class RegisterClosure(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: date
    shift: Shift
    total_sales: float
    cigarettes: float = 0.0
    gas: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def taxable_base(self) -> float:
        return max(0.0, self.total_sales - self.cigarettes - self.gas)

    @property
    def net_profit(self) -> float:
        return round(self.taxable_base * FACTOR, 2)

# Database Setup
engine = create_engine("sqlite:///caja.db", connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# FastAPI Application
app = FastAPI(title="Cash Register Closure - Bebidas Nachito")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# 1. Create a register closure
@app.post("/closures")
def create_closure(closure: RegisterClosure):
    with Session(engine) as session:
        session.add(closure)
        session.commit()
        session.refresh(closure)
        return {
            **closure.model_dump(),
            "net_profit": closure.net_profit,
        }


# 2. List closures / Filter by date or shift
@app.get("/closures")
def list_closures(closure_date: date | None = None, shift: Shift | None = None):
    with Session(engine) as session:
        query = select(RegisterClosure)
        if closure_date:
            query = query.where(RegisterClosure.date == closure_date)
        if shift:
            query = query.where(RegisterClosure.shift == shift)

        closures = session.exec(query).all()
        return [
            {**c.model_dump(), "net_profit": c.net_profit}
            for c in closures
        ]


# 3. Daily summary report
@app.get("/closures/day/{closure_date}")
def get_daily_summary(closure_date: date):
    with Session(engine) as session:
        query = select(RegisterClosure).where(RegisterClosure.date == closure_date)
        closures = session.exec(query).all()

        if not closures:
            raise HTTPException(status_code=404, detail="No closures recorded for this date")

        total_sales = sum(c.total_sales for c in closures)
        total_cigarettes = sum(c.cigarettes for c in closures)
        total_gas = sum(c.gas for c in closures)
        total_net_profit = sum(c.net_profit for c in closures)

        return {
            "date": closure_date,
            "recorded_shifts": [c.shift for c in closures],
            "total_sales": total_sales,
            "cigarettes_to_restock": total_cigarettes,
            "gas_to_restock": total_gas,
            "net_profit": round(total_net_profit, 2),
        }
