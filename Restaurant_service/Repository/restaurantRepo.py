from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from Model import model
from Schemas import schemas
from Hashing.hash import Hash


def register_restaurant(db: Session, request: schemas.restaurantBase):
    new_restaurant = model.Restaurant(
        restaurant_name=request.restaurant_name,
        restaurant_address=request.restaurant_address,
        restaurant_phone_number=request.restaurant_phone_number,
        restaurant_email=request.restaurant_email,
        password=Hash.bcrypt(request.password),
        restaurant_status=request.restaurant_status
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant




def login(db: Session,request :schemas.credentials):
    restaurant = db.query(model.Restaurant).filter(request.email == model.Restaurant.restaurant_email).first()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the email {request.email} is not available"
        )

    if not Hash.verify(restaurant.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    db.commit()
    db.refresh(restaurant)

    return restaurant






