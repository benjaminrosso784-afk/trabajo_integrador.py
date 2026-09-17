from fastapis import APIRouter
from pidantyc import basemodel

route = APIRouter(predix="/order")
tags=(["order"])

class order(basemodel):
    customer:str
    order:str
    value:int
    quantily:int
    total:float
    