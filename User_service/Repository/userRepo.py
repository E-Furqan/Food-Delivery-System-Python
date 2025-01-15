from logging import raiseExceptions

from sqlalchemy.orm import Session
from Model import model
from Schemas import schemas
from Hashing.hash import Hash
from fastapi import HTTPException, status


def createUser(request: schemas.User, db: Session):
    role_type = [role.role_type for role in request.roles]
    roles = db.query(model.Role).filter(model.Role.role_type.in_(role_type)).all()
    if len(roles) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one valid role is required."
        )

    new_user = model.User(
        full_name=request.full_name,
        email=request.email,
        password=Hash.bcrypt(request.password),
        user_name=request.user_name,
        phoneNumber=request.phoneNumber,
        address=request.address,
        roleStatus=request.roleStatus,
        activeRole=request.activeRole,
        roles=roles
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def fetchUser(id: int, db: Session):
    user = db.query(model.User).filter(model.User.user_id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    return user

def deleteUser(request: schemas.deleteUserInput, db: Session):
    # Fetch the user by email
    user = db.query(model.User).filter(model.User.email == request.email).first()

    # If the user doesn't exist, raise an exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the email {request.email} is not available"
        )

    # Verify the password
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Delete the user
    db.delete(user)
    db.commit()

    return {"detail": f"User with email {request.email} has been successfully deleted."}