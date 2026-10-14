from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "clave-de-prueba-2026"
header_scheme = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(header_scheme)):
    """Verifies that the API Key provided in the header matches the expected
    value."""
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")