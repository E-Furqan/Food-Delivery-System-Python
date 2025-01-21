from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read values from environment variables
SECRET_KEY = os.getenv("SECRET_KEY","Furqan")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
CREATE_TOKEN_URL = os.getenv("CREATE_TOKEN_URL","http://127.0.0.1:8084/authentication/create/token")
REFRESH_TOKEN_URL = os.getenv("REFRESH_TOKEN_URL","http://127.0.0.1:8084/authentication/refresh/token")
UPDATE_ORDER_STATUS_URL = os.getenv("UPDATE_ORDER_STATUS_URL","http://127.0.0.1:8082/order/update/status")