from threading import Timer

from fastapi import BackgroundTasks, APIRouter,HTTPException
from fastapi.responses import HTMLResponse, FileResponse,StreamingResponse
import coverage
import os
import glob
import shutil
import aiofiles
import random
from zoneinfo import ZoneInfo
import logging
from datetime import datetime

from EnviornmentVariable import enVVar


logger = logging.getLogger(__name__)
periodic_timer = None

dice = random.Random(os.urandom(8)).randint(0, 999999)
suffix = "%s.%s.%06d.%s.coverage" % (
    enVVar.POD_NAME,
    os.getpid(),
    dice,
    datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),
)


cov = coverage.Coverage(
    config_file='.coveragerc',
    data_suffix=suffix,
    data_file=os.path.join(enVVar.COVERAGE_DATA_FOLDER, "coverage"),
)


cov.load()
cov.start()

router = APIRouter(
    prefix="/coverage",
    tags=['Coverage']
)

def generate_coverage_report():
    cov.stop()
    cov.save()

    coverage_files = glob.glob(os.path.join(enVVar.COVERAGE_DATA_FOLDER, "*.coverage"))
    if not coverage_files:
        print(f"No coverage files found in {enVVar.COVERAGE_DATA_FOLDER}")
    else:
        print(f"Combining coverage files: {coverage_files}")

    combine_cov = coverage.Coverage(
        config_file='.coveragerc',
        data_file=os.path.join(enVVar.COVERAGE_DATA_FOLDER, "combined_coverage.coverage")
    )

    combine_cov.combine(data_paths=coverage_files,keep=True)

    combine_cov.html_report(directory=enVVar.COVERAGE_REPORT_DIRECTORY)

    cov.start()

def save_scheduled_coverage():
    print("saving")
    logger.info("saving scheduled coverage")
    cov.save()

def save_coverage():
    cov.stop()
    cov.combine()
    cov.save()

def schedule_periodic_save():
    global periodic_timer
    save_scheduled_coverage()
    periodic_timer=Timer(enVVar.CODE_COV_SAVE_SECONDS, schedule_periodic_save)
    periodic_timer.start()

@router.get("/gen_coverage_report")
async def generate_coverage_report_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_coverage_report)
    return {"message": "Coverage report is being generated asynchronously"}

@router.get("/download_cov", response_class=StreamingResponse)
async def download_coverage(background_tasks: BackgroundTasks):
    try:
        temp_dir = os.path.join("coverage_bundle")
        os.makedirs(temp_dir, exist_ok=True)

        coverage_files_dir = os.path.join(temp_dir, "coverage_data")
        shutil.copytree(enVVar.COVERAGE_DATA_FOLDER, coverage_files_dir, dirs_exist_ok=True)

        report_dir = os.path.join(temp_dir, "html_report")
        shutil.copytree(enVVar.COVERAGE_REPORT_DIRECTORY, report_dir, dirs_exist_ok=True)

        zip_file_path = os.path.join("code_coverage_bundle")
        shutil.make_archive(
            zip_file_path,
            "zip",
            root_dir=temp_dir
        )
        zip_file_full_path = f"{zip_file_path}.zip"

        async def file_stream():
            async with aiofiles.open(zip_file_full_path, "rb") as zip_file:
                while chunk := await zip_file.read(64 * 1024):  # 64KB chunks
                    yield chunk

        response = StreamingResponse(
            file_stream(),
            media_type="application/zip",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=code_coverage_bundle-"
                    f"{datetime.now(ZoneInfo('UTC')).timestamp()}.zip"
                )
            }
        )

        def delete_temp_file_folder():
            shutil.rmtree(temp_dir, ignore_errors=True)
            os.remove(zip_file_full_path)
            logger.info(f"deleted the temporary ZIP file and coverage bundle folder")

        background_tasks.add_task(delete_temp_file_folder)

        return response
    except Exception as error:
        logger.error(f"Failed to generate coverage ZIP: {error}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Failed to generate coverage ZIP",
                "errors": str(error)
            }
        )



@router.get("/", response_class=FileResponse)
async def serve_coverage_root():
    print("serve")
    full_path = os.path.join(enVVar.COVERAGE_REPORT_DIRECTORY, "index.html")
    if os.path.exists(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404, detail="Coverage report not generated yet")


@router.get("/{file_path:path}")
async def serve_coverage(file_path: str):
    print("Sdsa")
    full_path = os.path.join(enVVar.COVERAGE_REPORT_DIRECTORY, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    raise HTTPException(status_code=404, detail="File not found")



@router.on_event("shutdown")
async def shutdown_event():
    global periodic_timer
    print("saving when shutting down")
    logger.info("saving when shutting down coverage")
    if periodic_timer is not None:
        periodic_timer.cancel()  # Stop the Timer
        print("Periodic save timer cancelled")
    cov.stop()
    cov.save()