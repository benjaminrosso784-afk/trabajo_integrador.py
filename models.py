from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

DB_URL = "sqlite:///kiosko.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

    sales: Mapped[list["Sale"]] = relationship(back_populates="product")

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    payment_method: Mapped[str] = mapped_column(nullable=False)
    total: Mapped[float] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("[enlace sospechoso eliminado]"), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="sales")

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped