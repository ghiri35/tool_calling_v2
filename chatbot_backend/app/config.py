import os

DB_USER = os.getenv("DB_USER", "chatbotuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ghiri")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chatbotdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET_KEY = "your-secret-key"  # You can make this more secure later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
