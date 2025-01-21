from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read values from environment variables
FETCH_ITEM_URL = os.getenv("CREATE_TOKEN_URL","http://127.0.0.1:8081/restaurant/fetch/item/prices")
SECRET_KEY = os.getenv("SECRET_KEY","Furqan")
ALGORITHM = os.getenv("ALGORITHM", "HS256")