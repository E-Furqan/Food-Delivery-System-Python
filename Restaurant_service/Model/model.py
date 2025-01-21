from sqlalchemy import Column, Integer, String, Float, ForeignKey, Time
from sqlalchemy.orm import relationship
import datetime
from DatabaseConfig.databaseConfig import Base


class Item(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    item_description = Column(String, nullable=False)
    item_price = Column(Float, default=0)
    restaurant_id = Column(Integer, ForeignKey('restaurants.restaurant_id'), nullable=False)

    restaurant = relationship("Restaurant", back_populates="items")


class Restaurant(Base):
    __tablename__ = 'restaurants'

    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_name = Column(String, nullable=False)
    restaurant_address = Column(String, nullable=False)
    restaurant_phone_number = Column(String, nullable=False)
    restaurant_email = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    restaurant_status = Column(String)

    items = relationship("Item", back_populates="restaurant")
