import db
from sqlalchemy import select
from sqlalchemy.orm import Session

def get_products(category: str = None):
    """Retrieves all products from the database, optionally filtered by category."""
    with db.get_session() as session:        
        query = select(db.Product)
        if category:
            query = query.where(db.Product.category == category)
        query = session.scalars(query).all()
        return [product_to_dict(p) for p in query]

def product_to_dict(product: db.Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
    }

def sale_to_dict(sale: db.Sale) -> dict:
    return {
        "id": sale.id,
        "date": sale.date,
        "quantity": sale.quantity,
        "payment method": sale.payment_method,
        "means of payment": sale.payment_method,
        "total": sale.total,
    }

def expense_to_dict(expense: db.Expense) -> dict:
    return {
        "id": expense.id,
        "date": expense.date,
        "amount": expense.amount,
        "description": expense.description
    }

