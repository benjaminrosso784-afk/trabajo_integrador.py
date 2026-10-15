from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from db import Product, Sale, Expense, get_session, create_tables

def seed_database():
    create_tables()

    with get_session() as session:
        if session.scalars(select(Product)).first() is not None:
            print("Database already contains data. Skipping seed.")
            return
        
        products = [
            Product(name="Coca Cola 500ml", category="bebidas", price=1500.0),         
            Product(name="Agua Mineral 500ml", category="bebidas", price=1000.0),      
            Product(name="Cerveza Quilmes 473ml", category="bebidas", price=2200.0),   
            Product(name="Cerveza Quilmes 1L", category="bebidas", price=2800.0),       
            Product(name="Alfajor Jorgito", category="golosinas", price=800.0),        
            Product(name="Chocolate Milka", category="golosinas", price=1800.0),       
            Product(name="Caramelos Flynn Paff", category="golosinas", price=500.0),   
            Product(name="Chicles Beldent", category="golosinas", price=600.0),       
            Product(name="Galletitas Oreo", category="galletitas", price=1600.0),      
            Product(name="Papas Lays 100g", category="snacks", price=2500.0),         
            Product(name="Doritos 90g", category="snacks", price=2700.0),             
            Product(name="Cigarrillos Marlboro Box", category="cigarrillos", price=3500.0), 
            Product(name="Cigarrillos Philip Morris", category="cigarrillos", price=3200.0),
            Product(name="Papas Fritas Lay's", category="snacks", price=1800.0),       
            Product(name="Maní Salado", category="snacks", price=900.0),         
        ]
        session.add_all(products)
        session.commit()

        sales = [
            Sale(date="2026-09-10", quantity=2, payment_method="efectivo", total=3000.0, product_id=1),
            Sale(date="2026-09-10", quantity=1, payment_method="debito", total=1000.0, product_id=2),
            Sale(date="2026-09-10", quantity=3, payment_method="transferencia", total=2400.0, product_id=5),
            Sale(date="2026-09-10", quantity=1, payment_method="efectivo", total=2500.0, product_id=10),
            Sale(date="2026-09-10", quantity=2, payment_method="debito", total=3600.0, product_id=6),
            Sale(date="2026-09-11", quantity=1, payment_method="transferencia", total=2200.0, product_id=3),
            Sale(date="2026-09-11", quantity=4, payment_method="efectivo", total=2000.0, product_id=7),
            Sale(date="2026-09-11", quantity=2, payment_method="debito", total=5400.0, product_id=11),
            Sale(date="2026-09-12", quantity=3, payment_method="efectivo", total=1800.0, product_id=8),
            Sale(date="2026-09-12", quantity=2, payment_method="transferencia", total=3200.0, product_id=9),
            Sale(date="2026-09-10", quantity=1, payment_method="transferencia", total=3500.0, product_id=12),
            Sale(date="2026-09-10", quantity=1, payment_method="debito", total=2800.0, product_id=4),
            Sale(date="2026-09-11", quantity=1, payment_method="transferencia", total=3200.0, product_id=13),
            Sale(date="2026-09-11", quantity=2, payment_method="debito", total=3600.0, product_id=14),
            Sale(date="2026-09-11", quantity=1, payment_method="efectivo", total=900.0, product_id=15),
        ]
        session.add_all(sales)
        session.commit()

        expenses = [
            Expense(date="2026-09-10", description="Pago proveedor de hielo", amount=2000.0),
            Expense(date="2026-09-10", description="Compra de bolsas plasticas", amount=1500.0),
            Expense(date="2026-09-10", description="Articulos de limpieza", amount=3000.0),
            Expense(date="2026-09-11", description="Reposicion chicles", amount=4000.0),
            Expense(date="2026-09-11", description="Pago servicio de luz", amount=12000.0),
            Expense(date="2026-09-11", description="Cinta para embalar", amount=800.0),
            Expense(date="2026-09-12", description="Flete distribuida de gaseosas", amount=5000.0),
            Expense(date="2026-09-12", description="Abono servicio de internet", amount=8000.0),
            Expense(date="2026-09-12", description="Insumos de libreria", amount=2200.0),
            Expense(date="2026-09-12", description="Reparacion de exhibidora", amount=15000.0),
            Expense(date="2026-09-12", description="Pago proveedor de pan", amount=4500.0),
            Expense(date="2026-09-10", description="Retiro de caja chica", amount=3000.0),
            Expense(date="2026-09-11", description="Pago proveedor golosinas", amount=8500.0),
            Expense(date="2026-09-11", description="Mantenimiento de heladera", amount=5000.0),
        ]
        session.add_all(expenses)
        session.commit()
        
        print("Database initial seed completed successfully on kiosko.db!")

if __name__ == "__main__":
    seed_database()