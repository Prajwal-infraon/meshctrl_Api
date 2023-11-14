import subprocess
from pymongo import MongoClient
import re
from fastapi.responses import FileResponse
import json
from fastapi import HTTPException, status

js_file = "meshctrl.js"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["meshcentral"]
collection = db["meshcentral"]

def processForUrl(serial_number):
    node_id = getNodeID(serial_number)
    device_sharing_data = device_sharing(node_id)
    url_lst = find_url(device_sharing_data)
    if len(url_lst) > 0:
        return url_lst[0]
    else:
        device_sharing_data = device_sharing(node_id, url_avail = False)
        url_lst = find_url(device_sharing_data)
        return url_lst[0]
    
    
def getNodeID(serial_number):
    data = collection.find({"hardware.identifiers.bios_serial" : serial_number})
    if data:
        node_id = data[0].get("_id", None)
        return node_id[2:]
    else:
        return 0

    
def device_sharing(node_id, url_avail = True):
    if url_avail == True:
        command = f'node meshctrl DeviceSharing --id {node_id} --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
    elif url_avail == False:
        command = f'node meshctrl DeviceSharing --id {node_id} --add infraon_desktop --type desktop,terminal --consent prompt  --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)

        
def find_url(data):
    urls = re.findall(r'https://[^\s]+',data)
    url_lst = []
    for url in urls:
        url_lst.append(url[:-1])
    return url_lst


def getAgentexe(org_id : str ,architecture_id : str):
    group_id = ""
    collection = db["org_id"]
    try:
        query_2 = collection.find({'org_id' : org_id},{'org_id' : 1,'_id': 1})
        raw_query_res = list(query_2)
        if not raw_query_res: 
            command= f'node meshctrl adddevicegroup --name \'{org_id}\' --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
            else:
                group_id = result.stdout[9:]
                group_id = group_id.strip()
                collection.insert_one({"org_id":org_id,"mesh_id":group_id})
                command = f'node meshctrl  AgentDownload --id {group_id} --type {architecture_id} --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
                result_1 = subprocess.run(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                if not result_1.stderr:
                    res = result_1.stdout
                else:
                    res = None
                    return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
            return res 
        else:
            return HTTPException(detail=f"org_id : {org_id} Already exist.", status_code=status.HTTP_403_FORBIDDEN)
    except Exception as msg:
        print(msg)
        return HTTPException(detail="Exception in downloading Agent", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
           
        
def cmd_call():
    try:
        command = 'D:/remote_desktop_api/ InfraonRemoteAgent32-12345678.exe --fullinstall'
        print(command)
        result = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        print(result)
        return result
    except subprocess.CalledProcessError as e :
        print(e)

    