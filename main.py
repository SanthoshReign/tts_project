from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from db import Base, engine

from routers import user as user_router
from routers import team as team_router
from routers import admin as admin_router
from routers import client as client_router

app = FastAPI()

app.include_router(user_router.router)
app.include_router(admin_router.router)
app.include_router(team_router.router)
app.include_router(client_router.router)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins= [settings.FRONTEND_URL],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


# creating tables
Base.metadata.create_all(bind = engine)

@app.get("/")
def root():
    return {"status": "FastAPI running"}



