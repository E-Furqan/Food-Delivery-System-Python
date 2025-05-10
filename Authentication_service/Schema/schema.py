from typing import  Optional
from pydantic import BaseModel


class payload(BaseModel):
    id:int
    role:str


class token(BaseModel):
    access_token:str

class refresh_token(BaseModel):
    refresh_token:str
