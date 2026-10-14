from fastapi import FastAPI, Depends
from security import verify_api_key
from endpoints import router

app = FastAPI(
    title="Convenience Store Cash Closing API",
    description="Integrative Project - Management of Products, Sales, Expenses, and Daily Cash Closing",
    dependencies=[Depends(verify_api_key)],
)

app.include_router(router)