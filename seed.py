from sqlalchemy import select
from sqlalchemy.orm import Session
from main import Base, Product, Sale, Expense, engine

def seed_database():
    """Siembra la base de datos SQLite utilizando la misma conexión definida en main.py."""
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Evita sembrar dos veces si ya existen productos en kiosko.db
        if session.scalars(select(Product)).first() is not None:
            print("Database already contains data. Skipping seed.")
            return

        products = [
            Product(nombre="Coca Cola 500ml", categoria="bebidas", precio=1500.0),         
            Product(nombre="Agua Mineral 500ml", categoria="bebidas", precio=1000.0),      
            Product(nombre="Cerveza Quilmes 473ml", categoria="bebidas", precio=2200.0),   
            Product(nombre="Cerveza Quilmes 1L", categoria="bebidas", precio=2800.0),       
            Product(nombre="Alfajor Jorgito", categoria="golosinas", precio=800.0),        
            Product(nombre="Chocolate Milka", categoria="golosinas", precio=1800.0),       
            Product(nombre="Caramelos Flynn Paff", categoria="golosinas", precio=500.0),   
            Product(nombre="Chicles Beldent", categoria="golosinas", precio=600.0),       
            Product(nombre="Galletitas Oreo", categoria="galletitas", precio=1600.0),      
            Product(nombre="Papas Lays 100g", categoria="snacks", precio=2500.0),         
            Product(nombre="Doritos 90g", categoria="snacks", precio=2700.0),             
            Product(nombre="Cigarrillos Marlboro Box", categoria="cigarrillos", precio=3500.0), 
            Product(nombre="Cigarrillos Philip Morris", categoria="cigarrillos", precio=3200.0),
            Product(nombre="Papas Fritas Lay's", categoria="snacks", precio=1800.0),       
            Product(nombre="Maní Salado", categoria="snacks", precio=900.0),         
        ]
        session.add_all(products)
        session.commit()


        sales = [
            Sale(fecha="2026-09-10", cantidad=2, medio_pago="efectivo", total=3000.0, producto_id=1),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="debito", total=1000.0, producto_id=2),
            Sale(fecha="2026-09-10", cantidad=3, medio_pago="transferencia", total=2400.0, producto_id=5),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="efectivo", total=2500.0, producto_id=10),
            Sale(fecha="2026-09-10", cantidad=2, medio_pago="debito", total=3600.0, producto_id=6),
            Sale(fecha="2026-09-11", cantidad=1, medio_pago="transferencia", total=2200.0, producto_id=3),
            Sale(fecha="2026-09-11", cantidad=4, medio_pago="efectivo", total=2000.0, producto_id=7),
            Sale(fecha="2026-09-11", cantidad=2, medio_pago="debito", total=5400.0, producto_id=11),
            Sale(fecha="2026-09-12", cantidad=3, medio_pago="efectivo", total=1800.0, producto_id=8),
            Sale(fecha="2026-09-12", cantidad=2, medio_pago="transferencia", total=3200.0, producto_id=9),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="transferencia", total=3500.0, producto_id=12),
            Sale(fecha="2026-09-10", cantidad=1, medio_pago="debito", total=2800.0, producto_id=4),
            Sale(fecha="2026-09-11", cantidad=1, medio_pago="transferencia", total=3200.0, producto_id=13),
            Sale(fecha="2026-09-11", cantidad=2, medio_pago="debito", total=3600.0, producto_id=14),
            Sale(fecha="2026-09-11", cantidad=1, medio_pago="efectivo", total=900.0, producto_id=15),
        ]
        session.add_all(sales)


        expenses = [
            Expense(fecha="2026-09-10", concepto="Pago proveedor de hielo", monto=2000.0),
            Expense(fecha="2026-09-10", concepto="Compra de bolsas plasticas", monto=1500.0),
            Expense(fecha="2026-09-10", concepto="Articulos de limpieza", monto=3000.0),
            Expense(fecha="2026-09-11", concepto="Reposicion chicles", monto=4000.0),
            Expense(fecha="2026-09-11", concepto="Pago servicio de luz", monto=12000.0),
            Expense(fecha="2026-09-11", concepto="Cinta para embalar", monto=800.0),
            Expense(fecha="2026-09-12", concepto="Flete distribuida de gaseosas", monto=5000.0),
            Expense(fecha="2026-09-12", concepto="Abono servicio de internet", monto=8000.0),
            Expense(fecha="2026-09-12", concepto="Insumos de libreria", monto=2200.0),
            Expense(fecha="2026-09-12", concepto="Reparacion de exhibidora", monto=15000.0),
            Expense(fecha="2026-09-10", concepto="Pago proveedor de pan", monto=4500.0),
            Expense(fecha="2026-09-10", concepto="Retiro de caja chica", monto=3000.0),
            Expense(fecha="2026-09-11", concepto="Pago proveedor golosinas", monto=8500.0),
            Expense(fecha="2026-09-11", concepto="Mantenimiento de heladera", monto=5000.0),
        ]
        session.add_all(expenses)

        session.commit()
        print("Database initial seed completed successfully on kiosko.db!")

if __name__ == "__main__":
    seed_database()