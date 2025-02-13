from fastapi  import FastAPI
from Routes import auth_routes
import uvicorn

app=FastAPI()

app.include_router(auth_routes.router)

if __name__ == "__main__":

    uvicorn.run("main:app", host="localhost", port=8084, reload=True)