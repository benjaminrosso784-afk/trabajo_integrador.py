from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


API_KEY = "clave-de-prueba-2026"
header_scheme = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(header_scheme)):
    """Verifies that the provided API key matches the expected constant."""
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="API key invalida")


app = FastAPI(dependencies=[Depends(verify_api_key)])


DB_URL = "sqlite:///kiosko.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    categoria: Mapped[str] = mapped_column()
    precio: Mapped[float] = mapped_column()

    
    sales: Mapped[list["Sale"]] = relationship(back_populates="product")

class Sale(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[str] = mapped_column()
    cantidad: Mapped[int] = mapped_column()
    medio_pago: Mapped[str] = mapped_column()
    total: Mapped[float] = mapped_column()
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))

    
    product: Mapped["Product"] = relationship(back_populates="sales")

class Expense(Base):
    __tablename__ = "egresos"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[str] = mapped_column()
    concepto: Mapped[str] = mapped_column()
    monto: Mapped[float] = mapped_column()



@app.get("/productos")
def get_products(categoria: str = None):
    """Returns all products, optionally filtered by category."""
    with Session(engine) as session:
        query = select(Product)
        if categoria:
            query = query.where(Product.categoria == categoria)
        products = session.scalars(query).all()
        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "categoria": p.categoria,
                "precio": p.precio
            }
            for p in products
        ]


@app.get("/ventas/{id}")
def get_sale(id: int):
    """Returns details of a specific sale or 404 if not found."""
    with Session(engine) as session:
        sale = session.get(Sale, id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return {
            "id": sale.id,
            "fecha": sale.fecha,
            "cantidad": sale.cantidad,
            "medio_pago": sale.medio_pago,
            "total": sale.total,
            "producto_id": sale.producto_id
        }


@app.get("/productos/{id}/ventas")
def get_product_sales(id: int):
    """Returns all sales related to a specific product or 404 if product does not exist."""
    with Session(engine) as session:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return [
            {
                "id": s.id,
                "fecha": s.fecha,
                "cantidad": s.cantidad,
                "medio_pago": s.medio_pago,
                "total": s.total,
                "producto_id": s.producto_id
            }
            for s in product.sales
        ]

# 4. GET /egresos?fecha=2026-09-10
@app.get("/egresos")
def get_expenses(fecha: str = None):
    """Returns all expenses, optionally filtered by date."""
    with Session(engine) as session:
        query = select(Expense)
        if fecha:
            query = query.where(Expense.fecha == fecha)
        expenses = session.scalars(query).all()
        return [
            {
                "id": e.id,
                "fecha": e.fecha,
                "concepto": e.concepto,
                "monto": e.monto
            }
            for e in expenses
        ]

# 5. GET /caja/cierre?fecha=2026-09-10
@app.get("/caja/cierre")
def get_cash_closing(fecha: str):
    """Calculates daily cash closing metrics: totals, payment methods, expenses, and net balance."""
    with Session(engine) as session:
        sales = session.scalars(select(Sale).where(Sale.fecha == fecha)).all()
        expenses = session.scalars(select(Expense).where(Expense.fecha == fecha)).all()

        total_sales = sum(s.total for s in sales)
        total_expenses = sum(e.monto for e in expenses)

        by_payment_method = {
            "efectivo": round(sum(s.total for s in sales if s.medio_pago == "efectivo"), 2),
            "debito": round(sum(s.total for s in sales if s.medio_pago == "debito"), 2),
            "transferencia": round(sum(s.total for s in sales if s.medio_pago == "transferencia"), 2)
        }

        net_balance = total_sales - total_expenses

        return {
            "fecha": fecha,
            "total_vendido": round(total_sales, 2),
            "por_medio_pago": by_payment_method,
            "total_egresos": round(total_expenses, 2),
            "saldo_del_dia": round(net_balance, 2)
        }

# 6. POST /egresos
@app.post("/egresos", status_code=201)
async def create_expense(request: Request):
    """Creates a new expense record with manual Python validation (no Pydantic)."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Cuerpo de la solicitud invalido")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="El cuerpo debe ser un objeto JSON")

    fecha = data.get("fecha")
    concepto = data.get("concepto")
    monto = data.get("monto")

    # Manual field validations
    if not fecha or not isinstance(fecha, str):
        raise HTTPException(status_code=400, detail="Campo 'fecha' requerido y debe ser texto (YYYY-MM-DD)")
    if not concepto or not isinstance(concepto, str):
        raise HTTPException(status_code=400, detail="Campo 'concepto' requerido y debe ser texto")
    if monto is None or not isinstance(monto, (int, float)) or monto <= 0:
        raise HTTPException(status_code=400, detail="Campo 'monto' requerido y debe ser un numero mayor a 0")

    with Session(engine) as session:
        new_expense = Expense(
            fecha=fecha,
            concepto=concepto,
            monto=float(monto)
        )
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)

        return {
            "id": new_expense.id,
            "fecha": new_expense.fecha,
            "concepto": new_expense.concepto,
            "monto": new_expense.monto
        }
