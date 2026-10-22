import crud
from security import verify_api_key

from fastapi import FastAPI , HTTPException, Request, Depends

app = FastAPI(title="Kiosco API", dependencies=[Depends(verify_api_key)])

@app.get("/")
def welcome():
    return "Welcome to the API!"


@app.get("/products")
def get_products(category: str | None = None):
    """Retrieves all products, optionally filtered by category."""
    try:
        products = crud.get_products(category)
        return products
    except:
        raise HTTPException(status_code=500, detail="Database error")
        

@app.get("/sales/{id}")
def get_sale(id: int | None = None):
    """Retrieves details of a specific sale by ID or 404 if not found."""
    try:
        sale = crud.get_sale(id)
        return sale
    except ValueError as e:
        raise HTTPException(status_code=404, detail= str(e))
    except Exception as a:
        raise HTTPException(status_code=404, detail= str(a))

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
    """Retrieves a specific expenses by ID from the database."""
    try:
        expenses = crud.get_expenses(id)
        return expenses
    except Exception as e:
        print (str(e))
        raise HTTPException(status_code=500, detail="Database error")
    except ValueError as s:
        raise HTTPException(status_code=404, detail="Expence not found")


@app.get("/cash-closing")
def cash_closing(date: str):

    try:
        closing = crud.cash_closing(date)
        return closing
    except:
        raise HTTPException(status_code=500, datail="Database error")



