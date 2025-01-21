from fastapi import  APIRouter,Depends
from fastapi.security import APIKeyHeader
from DatabaseConfig.databaseConfig import get_db
from Schemas import schemas
from sqlalchemy.orm import Session
from Repository import itemRepo
from MiddleWare import middleware

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter(
    prefix="/restaurant",
    tags=['Restaurant']
)


@router.post('/add/item',response_model=schemas.item)
def add_item(request: schemas.itemBase, db:Session=Depends(get_db),token_payload: dict = Depends(middleware.validate_token)):
    return itemRepo.add_item_to_restaurant(db,request,int(token_payload['id']))

@router.post('/fetch/item/prices',response_model=list[schemas.items_with_price])
def fetch_item_price(request: schemas.orderd_items, db:Session=Depends(get_db)):
    return itemRepo.fetch_item(db,request)