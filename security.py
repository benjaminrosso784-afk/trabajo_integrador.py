import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv()
API_KEY = os.getenv("API_KEY")
header_scheme = APIKeyHeader(name="X-API-KEY")

def verify_api_key(key: str = Depends(header_scheme)):
    if API_KEY is None or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")