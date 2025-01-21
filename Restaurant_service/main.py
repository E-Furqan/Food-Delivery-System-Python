from fastapi import FastAPI
from Routes import restaurantRoutes, itemRoutes
from fastapi.openapi.utils import get_openapi
from Model import model
from DatabaseConfig.databaseConfig import engine

app= FastAPI()
model.Base.metadata.create_all(engine)

app.include_router(restaurantRoutes.router)
app.include_router(itemRoutes.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Food Delivery User Service",
        version="1.0.0",
        description="This is the User Service for the Food Delivery System.",
        routes=app.routes,
    )

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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8081)