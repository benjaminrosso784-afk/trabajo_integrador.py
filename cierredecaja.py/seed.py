import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Session, relationship

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


def seed_database():
    """Creates tables and populates initial sample data if tables are empty."""
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        existing_products = session.execute(select(Product)).scalars().all()
        if existing_products:
            print("Database already contains data. Seed skipped.")
            return

        products_data = [
            Product(nombre="Coca Cola 500ml", categoria="bebidas", precio=1500.0),
            Product(nombre="Agua Mineral 500ml", categoria="bebidas", precio=1000.0),
            Product(nombre="Cerveza Quilmes 1L", categoria="bebidas", precio=2800.0),
            Product(nombre="Alfajor Jorgito", categoria="golosinas", precio=800.0),
            Product(nombre="Chocolate Milka", categoria="golosinas", precio=2200.0),
            Product(nombre="Caramelos Flynn Paff", categoria="golosinas", precio=500.0),
            Product(nombre="Cigarrillos Marlboro Box", categoria="cigarrillos", precio=3500.0),
            Product(nombre="Cigarrillos Philip Morris", categoria="cigarrillos", precio=3200.0),
            Product(nombre="Papas Fritas Lay's", categoria="snack", precio=1800.0),
            Product(nombre="Maní Salado", categoria="snack", precio=900.0),
        ]
        session.add_all(products_data)
        session.commit()

        sales_data = [
            Sale(fecha="2026-09-10", cantidad=2, medio_pago="efectivo", total=3000.0, producto_id=1),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="debito", total=1000.0, producto_id=2),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="transferencia", total=3500.0, producto_id=7),
            Sale(fecha="2026-09-10", cantidad=3, medio_pago="efectivo", total=2400.0, producto_id=4),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="debito", total=2800.0, producto_id=3),
            Sale(fecha="2026-09-11", cantidad=2, medio_pago="efectivo", total=4400.0, producto_id=5),
            Sale(fecha="2026-09-11", cantidad=1, medio_pago="transferencia", total=3200.0, producto_id=8),
            Sale(fecha="2026-09-11", cantidad=2, medio_pago="debito", total=3600.0, producto_id=9),
            Sale(fecha="2026-09-11", cantidad=1, medio_pago="efectivo", total=900.0, producto_id=10),
            Sale(fecha="2026-09-11", cantidad=4, medio_pago="efectivo", total=2000.0, producto_id=6),
        ]
        session.add_all(sales_data)
        session.commit()

        expenses_data = [
            Expense(fecha="2026-09-10", concepto="Pago proveedor de pan", monto=4500.0),
            Expense(fecha="2026-09-10", concepto="Limpieza de local", monto=2000.0),
            Expense(fecha="2026-09-10", concepto="Reposición de hielo", monto=1500.0),
            Expense(fecha="2026-09-10", concepto="Retiro de caja chica", monto=3000.0),
            Expense(fecha="2026-09-10", concepto="Flete gaseosas", monto=2500.0),
            Expense(fecha="2026-09-11", concepto="Pago factura de luz", monto=12000.0),
            Expense(fecha="2026-09-11", concepto="Bolsas plásticas", monto=1800.0),
            Expense(fecha="2026-09-11", concepto="Pago proveedor golosinas", monto=8500.0),
            Expense(fecha="2026-09-11", concepto="Mantenimiento de heladera", monto=5000.0),
            Expense(fecha="2026-09-11", concepto="Artículos de librería", monto=1200.0),
        ]
        session.add_all(expenses_data)
        session.commit()

        print("Database seeded successfully with 10 records per table!")


if __name__ == "__main__":
    seed_database()