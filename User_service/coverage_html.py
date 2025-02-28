from fastapi import BackgroundTasks, APIRouter
import coverage
import os

# Initialize coverage
cov = coverage.Coverage(source=['.', 'Client','Model','Routes','Repository'])
cov.load()
cov.start()

router = APIRouter(
    prefix="/coverage",
    tags=['Coverage']
)

def generate_coverage_report():
    cov.save()
    cov.html_report(directory='coverage_report')

@router.get("/gen_coverage_report")
async def generate_coverage_report_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_coverage_report)
    return {"message": "Coverage report is being generated asynchronously"}

@router.get("/coverage")
async def serve_coverage():
    if os.path.exists("coverage_report/index.html"):
        with open("coverage_report/index.html", "r") as f:
            return f.read()
    return {"message": "No coverage report generated yet"}

@router.on_event("shutdown")
async def shutdown_event():
    cov.stop()
    cov.save()