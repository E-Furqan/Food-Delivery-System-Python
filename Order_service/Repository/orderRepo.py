from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from Model import model
from Schemas import schemas
from datetime import datetime


def createOrder(request: schemas.createOrder,total_bil, db: Session):
    # Create a new order
    new_order = model.Order(
        user_id=request.user_id,
        restaurant_id=request.restaurant_id,
        delivery_driver=request.delivery_driver,
        order_status=request.order_status,
        total_bill=total_bil
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)


    for item in request.items:

        existing_item = db.query(model.Item).filter(model.Item.item_id == item.item_id).first()

        if not existing_item:
            new_item = model.Item(item_id=item.item_id)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
        else:
            new_item = existing_item

        neworderid=new_order.order_id
        newitemid=new_item.item_id
        quantity=item.quantity

        try:

            print(f"neworderid {neworderid},  newitemid {newitemid}, quantity {quantity}")
            new_order_item = model.OrderItem(
                order_id=neworderid,
                item_id=newitemid,
                quantity=quantity
            )
            print("new order item ",new_order_item)
            db.add(new_order_item)
        except Exception as e:
            print("error is this ",e)

    db.commit()
    return new_order

def fetchOrder(order_id: int, db: Session):
    order = db.query(model.Order).filter(order_id == model.Order.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with the id {order_id} is not available")
    db.commit()

    return order


def fetchOrderBaseOnRole(request: schemas.update_order_status ,role ,db: Session):

    if "restaurant" == role:
        order = db.query(model.Order).filter(request.order_id == model.Order.order_id and request.id == model.Order.restaurant_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with the id {request.order_id} is not available for the restaurant with id {request.id}")
    elif role =="delivery_driver":
        order = db.query(model.Order).filter(request.order_id == model.Order.order_id and request.id == model.Order.delivery_driver).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with the id {request.order_id} is not available for the delivery driver with id {request.id}")
    elif role =="user":
        order = db.query(model.Order).filter(request.order_id == model.Order.order_id and request.id == model.Order.user_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with the id {request.order_id} is not available for the user with id {request.id}")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Invalid role for the token")


    db.commit()
    return order



def updateOrder(update_order : model.Order ,db: Session):
    db.merge(update_order)

    db.commit()

    db.refresh(update_order)

    return update_order