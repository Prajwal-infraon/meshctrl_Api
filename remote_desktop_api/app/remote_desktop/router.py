from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, HTMLResponse
from .controller import *

rdp_router = APIRouter()


@rdp_router.post("/get-url")
def getUrl(serial_number):
    try:
        url = processForUrl(serial_number)
        if url:
            return url
        else:
            HTMLResponse(content="Url Not Found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Exception in getting the getting the URL : {e}")

@rdp_router.post("/get-agent")
def getAgent(org_id:str,architecture_id:str):
    exe_agent = getAgentexe(org_id, architecture_id)
    return exe_agent


# @rdp_router.post("/cmd_call")
# def getAgent():
#     exe_agent = cmd_call()
#     return exe_agent


# from fastapi.responses import FileResponse


# @rdp_router.get("/download/")
# async def download_file():
#     file_path = "C:/Users/Praju/Downloads/meshaction_1.txt"
#     return FileResponse(file_path, media_type='application/octet-stream')
    