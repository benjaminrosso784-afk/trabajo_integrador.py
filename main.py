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

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Float, ForeignKey


CLAVE = "clave-de-prueba-2026"
header = APIKeyHeader(name="X-API-Key")


def verify_api_key(api_key: str = Depends(header)):
    """Validates the incoming X-API-Key header against the expected key."""
    if api_key != CLAVE:
        raise HTTPException(status_code=401, detail="API key invalida")


app = FastAPI(
    title="API Cierre de Caja - Kiosco",
    description="Proyecto Integrador Grupo 7 - Cierre de Caja",
    dependencies=[Depends(verify_api_key)],
)

DATABASE_URL = "sqlite:///cierre_caja.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    precio = Column(Float, nullable=False)

    sales = relationship("Sale", back_populates="product")


class Sale(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    medio_pago = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    product = relationship("Product", back_populates="sales")


class Expense(Base):
    __tablename__ = "egresos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String, nullable=False)
    concepto = Column(String, nullable=False)
    monto = Column(Float, nullable=False)


def product_to_dict(product: Product) -> dict:
    return {
        "id": product.id,
        "nombre": product.nombre,
        "categoria": product.categoria,
        "precio": product.precio,
    }


def sale_to_dict(sale: Sale) -> dict:
    return {
        "id": sale.id,
        "fecha": sale.fecha,
        "cantidad": sale.cantidad,
        "medio_pago": sale.medio_pago,
        "total": sale.total,
        "producto_id": sale.producto_id,
    }


def expense_to_dict(expense: Expense) -> dict:
    return {
        "id": expense.id,
        "fecha": expense.fecha,
        "concepto": expense.concepto,
        "monto": expense.monto,
    }



@app.get("/productos")
def get_products(categoria: str = None):
    """List products with optional category query parameter filter."""
    with Session(engine) as session:
        query = select(Product)
        if categoria:
            query = query.where(Product.categoria == categoria.lower())
        products = session.execute(query).scalars().all()
        return [product_to_dict(p) for p in products]


@app.get("/ventas/{id}")
def get_sale_by_id(id: int):
    """Retrieve details for a specific sale by ID."""
    with Session(engine) as session:
        sale = session.get(Sale, id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return sale_to_dict(sale)


@app.get("/productos/{id}/ventas")
def get_product_sales(id: int):
    """Retrieve all sales associated with a specific product ID."""
    with Session(engine) as session:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        sales = session.execute(select(Sale).where(Sale.producto_id == id)).scalars().all()
        return [sale_to_dict(s) for s in sales]



@app.get("/egresos")
def get_expenses(fecha: str = None):
    """List expenses with optional date query parameter filter."""
    with Session(engine) as session:
        query = select(Expense)
        if fecha:
            query = query.where(Expense.fecha == fecha)
        expenses = session.execute(query).scalars().all()
        return [expense_to_dict(e) for e in expenses]



@app.get("/caja/cierre")
def get_cash_close(fecha: str):
    """Calculate daily sales summary, payment method breakdown, total expenses, and balance."""
    with Session(engine) as session:

        sales = session.execute(select(Sale).where(Sale.fecha == fecha)).scalars().all()


        expenses = session.execute(select(Expense).where(Expense.fecha == fecha)).scalars().all()

        total_vendido = sum(s.total for s in sales)
        total_egresos = sum(e.monto for e in expenses)

        total_por_medio_pago = {
            "efectivo": sum(s.total for s in sales if s.medio_pago == "efectivo"),
            "debito": sum(s.total for s in sales if s.medio_pago == "debito"),
            "transferencia": sum(s.total for s in sales if s.medio_pago == "transferencia"),
        }

        saldo_dia = total_vendido - total_egresos

        return {
            "fecha": fecha,
            "total_vendido": round(total_vendido, 2),
            "total_por_medio_pago": {k: round(v, 2) for k, v in total_por_medio_pago.items()},
            "total_egresos": round(total_egresos, 2),
            "saldo_dia": round(saldo_dia, 2),
        }


@app.post("/egresos", status_code=201)
def create_expense(data: dict):
    """Create a new expense entry validating input payload manually."""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="El cuerpo debe ser un objeto JSON valido")


    required_fields = ["fecha", "concepto", "monto"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=400, detail=f"El campo '{field}' es obligatorio"
            )

    
    concepto = data["concepto"]
    if not isinstance(concepto, str) or not concepto.strip():
        raise HTTPException(
            status_code=400, detail="El campo 'concepto' debe ser un texto no vacio"
        )

    
    monto = data["monto"]
    if not isinstance(monto, (int, float)) or monto <= 0:
        raise HTTPException(
            status_code=400, detail="El campo 'monto' debe ser un numero positivo mayor a 0"
        )

    
    fecha = data["fecha"]
    if not isinstance(fecha, str) or not fecha.strip():
        raise HTTPException(
            status_code=400, detail="El campo 'fecha' debe ser un texto valido (YYYY-MM-DD)"
        )

    with Session(engine) as session:
        new_expense = Expense(
            fecha=fecha.strip(), concepto=concepto.strip(), monto=float(monto)
        )
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return expense_to_dict(new_expense)