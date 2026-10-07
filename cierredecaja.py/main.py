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