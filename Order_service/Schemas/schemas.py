from pydantic import BaseModel
from typing import List, Optional


class item(BaseModel):
    item_id: int

    class Config:
        orm_mode = True


class item_with_quantity(BaseModel):
    item_id: int
    quantity: int

    class Config:
        orm_mode = True

class items_with_price(BaseModel):
    item_id: int
    item_price: float
    class Config:
        orm_mode = True

class orderBase(BaseModel):
    user_id: int
    restaurant_id: int
    order_status: str
    total_bill: float
    delivery_driver: Optional[int] = 0

class createOrder(BaseModel):
    user_id: int
    restaurant_id: int
    order_status: str
    delivery_driver: Optional[int] = 0
    items: List[item_with_quantity]

    class Config:
        orm_mode = True


class orderd_items(BaseModel):
    item_ids: List[int]
    restaurant_id: int


class show_order(orderBase):
    items: List[item]


class update_order_status(BaseModel):
    order_id: int
    order_status: str
    id: int

    class Config:
        orm_mode = True