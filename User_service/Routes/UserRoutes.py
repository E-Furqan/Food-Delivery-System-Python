from fastapi import  APIRouter,Depends
from DatabaseConfig.databaseConfig import get_db
from Schemas import schemas
from Repository import userRepo
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/user",
    tags=['Users']
)

@router.post('/register/user')
def createUser(request: schemas.User, db:Session=Depends(get_db)):
    return userRepo.createUser(request, db)


@router.get(f'/fetch/user/{id}')
def fetchUser(id: int, db:Session=Depends(get_db)):
    return userRepo.fetchUser(id, db)


@router.delete('/delete/user')
def deleteUser(request: schemas.deleteUserInput, db:Session=Depends(get_db)):
    return userRepo.deleteUser(request, db)

