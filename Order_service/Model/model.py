from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DATETIME
from DatabaseConfig.databaseConfig import Base
from sqlalchemy.orm import relationship
import datetime


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    item_id = Column(Integer, ForeignKey('items.item_id'))
    quantity = Column(Integer)

    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")



class Item(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True, index=True)
    orders = relationship("Order", secondary="order_items", back_populates="items")

    order_items = relationship("OrderItem", back_populates="item")


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    delivery_driver = Column(Integer, default=0)
    order_status = Column(String(100), nullable=False)
    total_bill = Column(Float, nullable=False)
    time = Column(DATETIME, default=datetime.datetime.utcnow)

    items = relationship("Item", secondary="order_items", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

