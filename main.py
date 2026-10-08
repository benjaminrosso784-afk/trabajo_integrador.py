from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# 1. Configuración de Seguridad

API_KEY = "clave-de-prueba-2026"
header_scheme = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(header_scheme)):
    """Verifica que la API Key provista en el header coincida con la esperada."""
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="API key invalida")

app = FastAPI(
    title="API Cierre de Caja - Kiosco",
    description="Proyecto Integrador - Gestión de Productos, Ventas y Cierre de Caja",
    dependencies=[Depends(verify_api_key)],
)


# 2. Base de Datos Única (kiosko.db) y Modelos ORM

DB_URL = "sqlite:///kiosko.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(nullable=False)
    categoria: Mapped[str] = mapped_column(nullable=False)
    precio: Mapped[float] = mapped_column(nullable=False)

    sales: Mapped[list["Sale"]] = relationship(back_populates="product")

class Sale(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha: Mapped[str] = mapped_column(nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    medio_pago: Mapped[str] = mapped_column(nullable=False)
    total: Mapped[float] = mapped_column(nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="sales")

class Expense(Base):
    __tablename__ = "egresos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha: Mapped[str] = mapped_column(nullable=False)
    concepto: Mapped[str] = mapped_column(nullable=False)
    monto: Mapped[float] = mapped_column(nullable=False)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Funciones auxiliares de conversión a dict
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

# 3. Endpoints Nivel A


@app.get("/productos")
def get_products(categoria: str = None):
    """Devuelve todos los productos, opcionalmente filtrados por categoría."""
    with Session(engine) as session:
        query = select(Product)
        if categoria:
            query = query.where(Product.categoria.ilike(categoria))
        products = session.scalars(query).all()
        return [product_to_dict(p) for p in products]

@app.get("/ventas/{id}")
def get_sale(id: int):
    """Devuelve los detalles de una venta específica o 404 si no existe."""
    with Session(engine) as session:
        sale = session.get(Sale, id)
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return sale_to_dict(sale)

@app.get("/productos/{id}/ventas")
def get_product_sales(id: int):
    """Devuelve todas las ventas asociadas a un producto."""
    with Session(engine) as session:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return [sale_to_dict(s) for s in product.sales]

@app.get("/egresos")
def get_expenses(fecha: str = None):
    """Devuelve todos los egresos, opcionalmente filtrados por fecha."""
    with Session(engine) as session:
        query = select(Expense)
        if fecha:
            query = query.where(Expense.fecha == fecha)
        expenses = session.scalars(query).all()
        return [expense_to_dict(e) for e in expenses]

@app.get("/caja/cierre")
def get_cash_closing(fecha: str):
    """Calcula las métricas de cierre de caja diario: totales, medios de pago, egresos y saldo neto."""
    with Session(engine) as session:
        sales = session.scalars(select(Sale).where(Sale.fecha == fecha)).all()
        expenses = session.scalars(select(Expense).where(Expense.fecha == fecha)).all()

        total_sales = sum(s.total for s in sales)
        total_expenses = sum(e.monto for e in expenses)

        by_payment_method = {
            "efectivo": round(sum(s.total for s in sales if s.medio_pago == "efectivo"), 2),
            "debito": round(sum(s.total for s in sales if s.medio_pago == "debito"), 2),
            "transferencia": round(sum(s.total for s in sales if s.medio_pago == "transferencia"), 2),
        }

        net_balance = total_sales - total_expenses

        return {
            "fecha": fecha,
            "total_vendido": round(total_sales, 2),
            "por_medio_pago": by_payment_method,
            "total_egresos": round(total_expenses, 2),
            "saldo_del_dia": round(net_balance, 2),
        }

@app.post("/egresos", status_code=201)
async def create_expense(request: Request):
    """Crea un nuevo registro de egreso validando los datos del cuerpo JSON sin Pydantic."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Cuerpo de la solicitud invalido")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="El cuerpo debe ser un objeto JSON valido")

    required_fields = ["fecha", "concepto", "monto"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"El campo '{field}' es obligatorio")

    fecha = data.get("fecha")
    concepto = data.get("concepto")
    monto = data.get("monto")

    if not isinstance(fecha, str) or not fecha.strip():
        raise HTTPException(status_code=400, detail="El campo 'fecha' debe ser un texto valido (YYYY-MM-DD)")
    if not isinstance(concepto, str) or not concepto.strip():
        raise HTTPException(status_code=400, detail="El campo 'concepto' debe ser un texto no vacio")
    if not isinstance(monto, (int, float)) or monto <= 0:
        raise HTTPException(status_code=400, detail="El campo 'monto' debe ser un numero positivo mayor a 0")

    with Session(engine) as session:
        new_expense = Expense(
            fecha=fecha.strip(),
            concepto=concepto.strip(),
            monto=float(monto)
        )
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return expense_to_dict(new_expense)