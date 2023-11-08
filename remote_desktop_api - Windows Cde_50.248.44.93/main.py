from fastapi import FastAPI
from app.remote_desktop.router import rdp_router



app = FastAPI()

app.include_router(rdp_router, tags=["REMOTE-DESKTOP"])