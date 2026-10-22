import crud
from security import verify_api_key

from fastapi import FastAPI , HTTPException, Request, Depends

app = FastAPI(title="Kiosco API", dependencies=[Depends(verify_api_key)])

@app.get("/")
def welcome():
    return "Welcome to the API!"


@app.get("/products")
def get_products(category: str = None):
    """Retrieves all products, optionally filtered by category."""
    try:
        products = crud.get_products(category)
        return products
    except:
        raise HTTPException(status_code=500, detail="Database error")
        

@app.get("/sales/{id}")
def get_sale(id: int = None):
    """Retrieves details of a specific sale by ID or 404 if not found."""
    try:
        sale = crud.get_sale(id)
        return crud.sale_to_dict(sale)
    except:
        raise HTTPException(status_code=404, detail="Sale not found")

@app.get("/products/{id}/sales")
def get_product_sales(id: int = None):
    """Retrieves all sales associated with a specific product ID."""
    try:
        sales = crud.get_product_sales(id)
        return [crud.sale_to_dict(s) for s in sales]
    except:
        raise HTTPException(status_code=404, detail="Product not found ")
  
@app.get("/expenses")
def get_expenses(id: int = None):
    """Retrieves all expenses, optionally filtered by date (YYYY-MM-DD)."""
    try:
        expenses = crud.get_expenses(id)
        return expenses
    except Exception as e:
        print (str(e))
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/cash-closing")
def get_cash_closing(date: str):
    """Calculates daily cash closing metrics: total sales, payment method breakdown, total expenses, and net balance."""
    with Session(engine) as session:
        sales = session.scalars(select(Sale).where(Sale.date == date)).all()
        expenses = session.scalars(select(Expense).where(Expense.date == date)).all()

        total_sales = sum(s.amount for s in sales)
        total_expenses = sum(e.amount for e in expenses)

        by_payment_method = {
            "cash": round(sum(s.amount for s in sales if s.payment_method == "cash"), 2),
            "debit": round(sum(s.amount for s in sales if s.payment_method == "debit"), 2),
            "transfer": round(sum(s.amount for s in sales if s.payment_method == "transfer"), 2),
        }

        net_balance = total_sales - total_expenses

        return {
            "date": date,
            "total_sales": round(total_sales, 2),
            "by_payment_method": by_payment_method,
            "total_expenses": round(total_expenses, 2),
            "daily_balance": round(net_balance, 2),
        }

@app.post("/expenses", status_code=201)
async def create_expense(request: Request):
    """Creates a new expense record with manual JSON parsing and validation."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    required_fields = ["date", "concept", "amount"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: '{field}'")

    date = data.get("date")
    concept = data.get("concept")
    amount = data.get("amount")

    if not isinstance(date, str) or not date.strip():
        raise HTTPException(status_code=400, detail="Field 'date' must be a valid non-empty string (YYYY-MM-DD)")
    if not isinstance(concept, str) or not concept.strip():
        raise HTTPException(status_code=400, detail="Field 'concept' must be a non-empty string")
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise HTTPException(status_code=400, detail="Field 'amount' must be a positive number greater than 0")

    with Session(engine) as session:
        new_expense = Expense(
            date=date.strip(),
            concept=concept.strip(),
            amount=float(amount)
        )
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return expense_to_dict(new_expense)
