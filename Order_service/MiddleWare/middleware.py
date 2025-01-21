from fastapi import Request, HTTPException, status
from functools import wraps
import jwt
from EnviornmentVariable import enVVar

SECRET_KEY = enVVar.SECRET_KEY
ALGORITHM = enVVar.ALGORITHM


def validate_token(request: Request):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing"
        )

    try:
        token = token.split(" ")[1] if token.startswith("Bearer ") else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("id")
        role_type = payload.get("role")

        print(f"Authenticated restaurant ID: {user_id}, Role: {role_type}")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
