from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Read values from environment variables
SECRET_KEY = os.getenv("SECRET_KEY","Furqan")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
