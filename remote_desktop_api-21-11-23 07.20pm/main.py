from fastapi import FastAPI
from app.remote_desktop.router import rdp_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)



app.include_router(rdp_router, tags=["REMOTE-DESKTOP"])
