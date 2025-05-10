from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read values from environment variables
SECRET_KEY = os.getenv("SECRET_KEY","Furqan")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
CREATE_TOKEN_URL = os.getenv("CREATE_TOKEN_URL","http://localhost:8084/authentication/create/token")
REFRESH_TOKEN_URL = os.getenv("REFRESH_TOKEN_URL","http://127.0.0.1:8084/authentication/refresh/token")
UPDATE_ORDER_STATUS_URL = os.getenv("UPDATE_ORDER_STATUS_URL","http://127.0.0.1:8082/order/update/status")
COVERAGE_REPORT_DIRECTORY = os.getenv("COVERAGE_REPORT_DIRECTORY","coverage_report")
POD_NAME = os.getenv("POD_NAME", "unknown_pod")
COVERAGE_DATA_FOLDER = os.getenv("COVERAGE_DATA_FOLDER","coverage_data")
CODE_COV_SAVE_SECONDS= float(os.getenv("CODE_COV_SAVE_SECONDS",60))