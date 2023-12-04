from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, FileResponse
from .controller import *
from .models import * 
from .utility import *
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
    exe_agent = getAgentexe(exe_info)
    return exe_agent


@rdp_router.get("/get-file")
async def downloadAgent(file_name):
    file_name = decode_file_name(file_name)
    filepath =f'C:/Users/infraon/Desktop/remote_desktop_api/Agents/{file_name}'
    return FileResponse(filepath, media_type='application/octet-stream',filename=file_name)

@rdp_router.get("/check-power")
async def checkpower(group_id,device_id):
    status = powcheck(group_id,device_id)
    return status