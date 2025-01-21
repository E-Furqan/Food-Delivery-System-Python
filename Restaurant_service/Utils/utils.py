from Schemas import schemas


def create_token_payload_obj(id : int, role_type : str):

    payload=schemas.auth_payload(id=id,role=role_type)

    return  payload

def create_order_payload_obj(order_details:schemas.order_details,restaurant_id:int):
    payload = schemas.order_payload(id=restaurant_id,
                                    order_id=order_details.order_id,order_status=order_details.order_status)

    return payload