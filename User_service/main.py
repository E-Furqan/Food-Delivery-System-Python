from fastapi import FastAPI,BackgroundTasks
from fastapi.openapi.utils import get_openapi

from Model import model
from DatabaseConfig.databaseConfig import engine,get_db
from Routes import userRoutes
from Repository import rolesRepo
import coverage_html

app = FastAPI()

model.Base.metadata.create_all(engine)


@app.get("/")
def read_root():
    return {"message": "API is working!"}

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    rolesRepo.create_default_roles(db)


app.include_router(userRoutes.router)
app.include_router(coverage_html.router)

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


# @app.get("/coverage-report/tracker")
# async def get_coverage_report():
#     tracker.cleanup_old_data()
#     report = tracker.get_hourly_report()
#
#     return report




# import coverage
# import asyncio
# import os
#
# # Initialize coverage
# cov = coverage.Coverage(source=['.'])  # Track coverage for the current directory
# cov.start()
#
#
#
#
# def generate_coverage_report():
#     # Stop coverage momentarily to save data
#     cov.stop()
#     cov.save()
#
#     # Generate HTML report
#     cov.html_report(directory='coverage_report')
#
#     # Restart coverage for ongoing tracking
#     cov.start()
#
# # Coverage report endpoint
# @app.get("/get_coverage_report")
# async def get_coverage_report(background_tasks: BackgroundTasks):
#     # Run report generation in the background
#     background_tasks.add_task(generate_coverage_report)
#     return {"message": "Coverage report is being generated asynchronously"}
#
# # Optional: Serve the coverage report
# @app.get("/coverage")
# async def serve_coverage():
#     if os.path.exists("coverage_report/index.html"):
#         with open("coverage_report/index.html", "r") as f:
#             return f.read()
#     return {"message": "No coverage report generated yet"}
#
# # Ensure coverage is saved on shutdown
# @app.on_event("shutdown")
# async def shutdown_event():
#     cov.stop()
#     cov.save()