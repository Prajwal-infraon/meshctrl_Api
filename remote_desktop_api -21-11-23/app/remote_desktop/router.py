from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, HTMLResponse
from .controller import *
from .models import * 

rdp_router = APIRouter()


@rdp_router.post("/get-url")
def getUrl(node_info : NodeInfoRequest):
    url = ""
    try:
        url = processForUrl(node_info)
    except Exception as e:
        print(">>>>",e)
    return JSONResponse(url)

@rdp_router.post("/get-agent")
def getAgent(exe_info : AgentExeRequest):
    print(exe_info)
    exe_agent = getAgentexe(exe_info)
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
    