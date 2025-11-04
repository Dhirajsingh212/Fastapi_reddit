import os

class Settings:
    JWT_SECRET = os.getenv("JWT_SECRET", "sc3rt")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_LOCATION = os.getenv("JWT_LOCATION", "headers")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DATABASE_URL = os.getenv("DATABASE_URL","postgresql://postgres:mysecretpassword@localhost:5432/mydatabase")

setting = Settings()
