import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from .config import JWT_SECRET, JWT_EXPIRE_HOURS

def hash_password(password: str):
    password = password.lower().encode()
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.lower().encode(), hashed.encode())

def create_session_token(token: str):
    payload = {
        "token": token,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_session_token(session_token: str):
    try:
        return jwt.decode(session_token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session")