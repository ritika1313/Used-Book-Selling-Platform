from fastapi import Header, HTTPException

# In production, you add this in .env 
API_KEY ="secret123"

def verify_api_key(x_api_key: str = Header(...)):
    """Verify the API Key from the request header."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key
