from fastapi import  APIRouter,Depends,HTTPException, status,Request
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from DatabaseConfig.databaseConfig import get_db
from Schemas import schemas
from Repository import userRepo
from Client import authClient,orderClient
from Utils import utils
from MiddleWare import middleware
from decorators import track_coverage

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter(
    prefix="/user",
    tags=['Users']
)



@router.post('/register/user')
@track_coverage
async  def createUserEndpoint(request: Request, user: schemas.User, db: Session = Depends(get_db)):
    try:
        print("testing")
        print("testing")
        result = await userRepo.createUser(user, db)
        return result
    except HTTPException as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content=e.detail)


@router.post('/login')
@track_coverage
def loginEndpoint(request: Request,Credentials: schemas.Credentials, db:Session=Depends(get_db)):
    try:
        print(f"Tracking endpoint: {request.url.path}")
        user = userRepo.login(Credentials, db)
        payload = utils.create_token_payload_obj(user.user_id, user.activeRole)
        print("payload", payload)
        response = authClient.create_token(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in authentication service : {e}"
        )

    return


@router.post('/refresh/token')
def refresh_tokenEndpoint(request: schemas.refresh_token):

    try:
        response = authClient.refresh_token(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error in authentication service : {e}"
        )


@router.put('/delete/user')
def deleteUserEndpoint(request: schemas.Credentials, db:Session=Depends(get_db), token_payload: dict = Depends(middleware.validate_token)):
    return userRepo.deleteUser(request, db)


@router.get(f'/fetch/user',response_model=schemas.User)
def fetchUserEndpoint(db:Session=Depends(get_db), token_payload: dict = Depends(middleware.validate_token)):
    return userRepo.fetchUser(token_payload['id'], db)

@router.put(f'/update/order/status',response_model=schemas.User)
def update_order_statusEndpoint(
    request: schemas.order_details,
    token_payload: dict = Depends(middleware.validate_token)
):
    """Update order status with proper error handling."""
    order_payload = utils.create_order_payload_obj(request, token_payload['id'])

    try:
        response = orderClient.update_order_status(order_payload, token_payload["token"])
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in order service: {str(e)}"
        )