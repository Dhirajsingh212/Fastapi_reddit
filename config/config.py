import os

class Settings:
    JWT_SECRET = os.getenv("JWT_SECRET", "sc3rt")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_LOCATION = os.getenv("JWT_LOCATION", "headers")
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./database.db")

setting = Settings()
