from pydantic import BaseModel

class ExpenceCreate(BaseModel):
    date: str 
    amount: float 
    description: str | None = None