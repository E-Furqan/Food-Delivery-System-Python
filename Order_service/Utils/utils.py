from Schemas import schemas




def create_ordered_items_obj(order_data: schemas.createOrder):
    ordered_items = schemas.orderd_items(
        item_ids=[item.item_id for item in order_data.items],
        restaurant_id=order_data.restaurant_id
    )

    return ordered_items
