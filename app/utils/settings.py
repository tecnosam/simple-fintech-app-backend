import os
from dotenv import load_dotenv


load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test")
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')


DATABASE_URI = os.getenv("DATABASE_URI")

