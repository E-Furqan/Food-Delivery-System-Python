import coverage_routes
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from Model import model
from DatabaseConfig.databaseConfig import engine,get_db
from Routes import userRoutes
from Repository import rolesRepo


app = FastAPI()

model.Base.metadata.create_all(engine)


@app.get("/")
def read_root():
    return {"message": "API is working!"}

@app.on_event("startup")
async def on_startup():
    db = next(get_db())
    await rolesRepo.create_default_roles(db)


app.include_router(userRoutes.router)
app.include_router(coverage_routes.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Food Delivery User Service",
        version="1.0.0",
        description="This is the User Service for the Food Delivery System.",
        routes=app.routes,
    )

    # Add the security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


