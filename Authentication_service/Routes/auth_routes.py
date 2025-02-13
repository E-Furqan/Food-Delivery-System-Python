from http.client import HTTPException

from fastapi import FastAPI,Depends,APIRouter
from oauthlib.openid.connect.core.tokens import JWTToken
from Schema import schema
from EnvironmentVariable import envVar
import jwt
from datetime import datetime, timedelta

SECRET_KEY = envVar.SECRET_KEY
ALGORITHM = envVar.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = envVar.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/authentication",
    tags=['Authentication']
)

@router.post("/create/token")
def create_token(data: schema.payload):
    to_encode = data.dict()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    JWTToken={"access_token":encoded_access_token,"refresh_token":encoded_refresh_token}

    return JWTToken

@router.post("/refresh/token")
def refresh_access_token(request: schema.refresh_token):
    try:
        # Decode and validate refresh token
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if "exp" in payload and datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token has expired")

        # Generate new access token
        user_data = {key: payload[key] for key in payload if key != "exp"}  # Exclude expiration
        access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        user_data.update({"exp": access_expire})
        new_access_token = jwt.encode(user_data, SECRET_KEY, algorithm=ALGORITHM)

        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/decode/token")
def decode_access_token(token: schema.token):
    try:
        payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.JWTError:
        raise Exception("Invalid token")