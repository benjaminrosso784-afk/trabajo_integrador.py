import db
from sqlalchemy import select
from sqlalchemy.orm import Session
from validation import ExpenceCreate


def get_products(category: str = None):
    """Retrieves all products from the database, optionally filtered by category."""
    with db.get_session() as session:        
        query = select(db.Product)
        if category:
            query = query.where(db.Product.category == category)
        query = session.scalars(query).all()
        return [product_to_dict(p) for p in query]
    
def get_sale(id: int):
    """Retrieves a specific sale by ID from the database."""
    with db.get_session() as session:
            sale = session.get(db.Sale, id)
            if not sale:
                raise ValueError("Sale not found")
            return sale_to_dict(sale)

def get_expenses(id: int):
    """Retrieves a specific expenses by ID from the database."""
    with db.get_session() as session:
        query = select(db.Expense)
        if id:
            query = query.where(db.Expense.id == id)
        expenses = session.scalars(query).all()
        return [expense_to_dict(e) for e in expenses]

def cash_closing(date: str):
    "Calculates daily cash closing metrics: total sales, payment method breakdown, total expenses, and net balance."
    with db.get_session() as session:
        sales = session.scalars(select(db.Sale).where(db.Sale.date == date)).all()
        expenses = session.scalars(select(db.Expense).where(db.Expense.date == date)).all()

        total_sales = sum(s.total for s in sales)
        total_expenses = sum(e.amount for e in expenses)

        by_payment_method = {
            "efectivo": round(sum(s.total for s in sales if s.payment_method == "efectivo"), 2),
            "debito": round(sum(s.total for s in sales if s.payment_method == "debito"), 2),
            "transferencia": round(sum(s.total for s in sales if s.payment_method == "transferencia"), 2)
        }

        net_balance = total_sales - total_expenses

        return {
            "date": date,
            "total_sales": round(total_sales, 2),
            "by_payment_method": (by_payment_method),
            "total_expenses": round(total_expenses, 2),
            "daily_balance": round(net_balance, 2),
            }

def expense_create(expense_data: ExpenceCreate):
    with db.get_session() as s:
        query = select(db.Expense).where(
            db.Expense.date == expense_data.date,
            db.Expense.amount == expense_data.amount,
            db.Expense.description == expense_data.description
        )
        existing = s.scalars(query).first()
        
        if existing:
            raise ValueError("Expense already exists  ")

        new_expense = db.Expense(
            date=expense_data.date,
            amount=expense_data.amount,
            description=expense_data.description
        )
        s.add(new_expense)
        s.commit()
        s.refresh(new_expense)
        return expense_to_dict(new_expense)
    

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
        "total": sale.total
    }

def expense_to_dict(expense: db.Expense) -> dict:
    return {
        "id": expense.id,
        "date": expense.date,
        "amount": expense.amount,
        "description": expense.description
        
    }