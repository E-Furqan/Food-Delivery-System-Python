from fastapi import FastAPI
from Routes import orderRoutes
from Model import model
from DatabaseConfig.databaseConfig import engine
import uvicorn

app= FastAPI()

app.include_router(orderRoutes.router)

model.Base.metadata.create_all(engine)

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True,host="localhost", port=8082)