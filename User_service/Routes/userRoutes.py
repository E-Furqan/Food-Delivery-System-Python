from fastapi import  APIRouter,Depends,HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from DatabaseConfig.databaseConfig import get_db
from Schemas import schemas
from Repository import userRepo
from Client import authClient,orderClient
from Utils import utils
from MiddleWare import middleware

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter(
    prefix="/user",
    tags=['Users']
)

@router.post('/register/user')
def createUser(request: schemas.User, db:Session=Depends(get_db)):
    print("request received")
    return userRepo.createUser(request, db)


@router.post('/login')
def login(request: schemas.Credentials, db:Session=Depends(get_db)):
    user = userRepo.login(request, db)
    payload = utils.create_token_payload_obj(user.user_id, user.activeRole)

    try:
        response = authClient.create_token(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in authentication service : {e}"
        )

    return

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


@router.delete('/delete/user')
def deleteUser(request: schemas.Credentials, db:Session=Depends(get_db), token_payload: dict = Depends(middleware.validate_token)):
    return userRepo.deleteUser(request, db)


@router.get(f'/fetch/user',response_model=schemas.User)
def fetchUser(db:Session=Depends(get_db), token_payload: dict = Depends(middleware.validate_token)):
    return userRepo.fetchUser(token_payload['id'], db)



@router.put(f'/update/order/status',response_model=schemas.User)
def order_status(request: schemas.order_details,token_payload: dict = Depends(middleware.validate_token)):
    print("token :",token_payload["token"])
    order_payload = utils.create_order_payload_obj(request,token_payload['id'])

    try:
        response = orderClient.update_order_status(order_payload,token_payload["token"])
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in order service : {e}"
        )
