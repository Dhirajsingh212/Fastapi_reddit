from fastapi import FastAPI

from database.db import engine
from routers import users, posts
from database import models
app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Hello testing"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
