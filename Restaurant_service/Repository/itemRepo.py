from sqlalchemy.orm import Session
from Model import model
from Schemas import schemas


def add_item_to_restaurant(db: Session,request :schemas.itemBase , restaurant_id: int):
    restaurant = db.query(model.Restaurant).filter(restaurant_id == model.Restaurant.restaurant_id).first()

    if not restaurant:
        raise ValueError("Restaurant with the given ID does not exist.")


    new_item = model.Item(
        item_name=request.item_name,
        item_description=request.item_description,
        item_price=request.item_price,
        restaurant_id=restaurant_id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


def fetch_item(db: Session,request :schemas.orderd_items):
    restaurant = db.query(model.Restaurant).filter(request.restaurant_id == model.Restaurant.restaurant_id).first()

    if not restaurant:
        raise ValueError("Restaurant with the given ID does not exist.")

    items = db.query(model.Item.item_id, model.Item.item_price) \
        .filter(
        model.Item.item_id.in_(request.item_ids),
        request.restaurant_id == model.Item.restaurant_id
    ).all()

    db.commit()

    return items

