from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .controller import get_connection_url

rdp_router = APIRouter()

# from pydantic import BaseModel
# class AssetInfo (BaseModel):     
#     serial_number:str

@rdp_router.post("/get-url")
def getUrl(asset_data: dict):
    print(asset_data)
    url = get_connection_url(asset_data)
    return JSONResponse({"data": url})

