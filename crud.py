import db



def product_to_dict(product: db.Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price
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

