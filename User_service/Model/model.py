from sqlalchemy import Column,Integer,String,ForeignKey,Table
from DatabaseConfig.databaseConfig import Base
from sqlalchemy.orm import relationship

# Association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.role_id'), primary_key=True)
)



class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    full_name=Column(String)
    user_name=Column(String)
    password=Column(String)
    email=Column(String)
    phoneNumber=Column(Integer)
    address=Column(String)
    roleStatus=Column(String)
    activeRole=Column(String)
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True, index=True)
    role_type = Column(String)
    users = relationship("User", secondary=user_roles, back_populates="roles")
