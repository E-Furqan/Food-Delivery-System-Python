from fastapi import  APIRouter,Depends,HTTPException, status
from fastapi.security import APIKeyHeader
from DatabaseConfig.databaseConfig import get_db
from Repository import orderRepo
from MiddleWare import middleware
from Schemas import schemas
from sqlalchemy.orm import Session
from Utils import utils,constants
from Client import restaurantClient

authorization_scheme = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter(
    prefix="/order",
    tags=['Order']
)

@router.post('/create/order',response_model=schemas.show_order)
def createOrder(request: schemas.createOrder, db:Session=Depends(get_db)):
    ordered_items=utils.create_ordered_items_obj(request)
    response=restaurantClient.fetch_item_prices(ordered_items)
    print("response; ",response)
    total_bill = 0.0

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No item found with the given item ids")

    for item in request.items:
        item_price = next((item_price['item_price'] for item_price in response if item_price['item_id'] == item.item_id), 0)
        total_bill += item_price * item.quantity

    return orderRepo.createOrder(request,total_bill, db)


@router.put('/update/status')
def updateOrderStatus(request: schemas.update_order_status, db:Session=Depends(get_db)
                      ,token_payload : dict = Depends(middleware.validate_token)):

    role= token_payload['role']

    try:
        order = orderRepo.fetchOrderBaseOnRole(request,role, db)
    except Exception as e:
        return e

    try:
        if request.order_status.lower() =="cancelled":
            new_status= "Cancelled"
        else:
            new_status= constants.mapper[role][order.order_status]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid status for the order: {e}")


    order.order_status = new_status

    return orderRepo.updateOrder(order,db)




