from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, HTMLResponse,Response
from .controller import *
from .models import * 

rdp_router = APIRouter()


@rdp_router.post("/get-url")
def getUrl(node_info : NodeInfoRequest):
    url = None
    try:
        url = processForUrl(node_info)
    except Exception as e:
        print(">>>>",e)
    return url

@rdp_router.post("/get-agent")
def getAgent(org_info :getagentexe):
    exe_agent= None
    try:
        exe_agent = getAgentexe(org_info)
    except Exception as e:
        print(">>>>>",e)
    return exe_agent

@rdp_router.get("/get-file")
async def downloadAgent(file_name):
    file_name = decode_file_name(file_name)
    print("@@@@@@@@@@@",file_name)
    filepath =f'D:/remote_desktop_api/Agents/{file_name}'
    return FileResponse(filepath, media_type='application/octet-stream',filename=file_name)
