from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .controller import processForUrl

rdp_router = APIRouter()


@rdp_router.post("/get-url")
def getUrl(serial_number):
    url = processForUrl(serial_number)
    return url

