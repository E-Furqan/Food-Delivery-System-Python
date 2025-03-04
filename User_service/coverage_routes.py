from fastapi import BackgroundTasks, APIRouter,HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import coverage
import os

from EnviornmentVariable import enVVar

cov = coverage.Coverage(config_file='.coveragerc',
                        data_file=enVVar.COVERAGE_DATA)
cov.load()
cov.start()

router = APIRouter(
    prefix="/coverage",
    tags=['Coverage']
)

def generate_coverage_report():
    cov.stop()
    cov.combine()
    cov.save()
    cov.html_report(directory=enVVar.COVERAGE_DIRECTORY)
    cov.start()

@router.get("/gen_coverage_report")
async def generate_coverage_report_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_coverage_report)
    return {"message": "Coverage report is being generated asynchronously"}

@router.get("/", response_class=FileResponse)
async def serve_coverage_root():
    full_path = os.path.join(enVVar.COVERAGE_DIRECTORY, "index.html")
    if os.path.exists(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404, detail="Coverage report not generated yet")

@router.get("/{file_path:path}")
async def serve_coverage(file_path: str):
    full_path = os.path.join(enVVar.COVERAGE_DIRECTORY, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404, detail="File not found")

@router.on_event("shutdown")
async def shutdown_event():
    cov.stop()
    cov.save()