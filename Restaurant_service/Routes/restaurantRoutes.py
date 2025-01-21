from fastapi import  APIRouter,Depends,HTTPException, status
from fastapi.security import APIKeyHeader
from DatabaseConfig.databaseConfig import get_db
from Schemas import schemas
from sqlalchemy.orm import Session
from Repository import restaurantRepo
from MiddleWare import middleware
from Client import authClient,orderClient
from Utils import utils

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter(
    prefix="/restaurant",
    tags=['Restaurant']
)

@router.post('/register/restaurant',response_model=schemas.restaurant)
def register_restaurant(request: schemas.restaurantBase, db:Session=Depends(get_db)):
    return restaurantRepo.register_restaurant(db,request)


@router.post('/login')
def login(request: schemas.credentials, db:Session=Depends(get_db)):
    restaurant = restaurantRepo.login(db, request)
    payload = utils.create_token_payload_obj(restaurant.restaurant_id,"restaurant")

    try:
        response = authClient.create_token(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in authentication service : {e}"
        )


@router.post('/refresh/token')
def refresh_token(request: schemas.refresh_token):
    try:
        response = authClient.refresh_token(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in authentication service : {e}"
        )



def order_status(request: schemas.order_details,token_payload: dict = Depends(middleware.validate_token)):

    token = token_payload['token']
    order_payload = utils.create_order_payload_obj(request,token_payload['id'])

    try:
        response = orderClient.update_order_status(order_payload,token)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in order service : {e}"
        )
