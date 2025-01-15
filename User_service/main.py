from fastapi import FastAPI
from Model import model
from DatabaseConfig.databaseConfig import engine,get_db
from Routes import UserRoutes
from Repository import RolesRepo

app = FastAPI()


model.Base.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    RolesRepo.create_default_roles(db)



app.include_router(UserRoutes.router)
