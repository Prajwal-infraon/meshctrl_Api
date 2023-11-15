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

def fetchUrl(serial_number):
    node_id = getNodeID(serial_number)
    if node_id != 0:
        device_sharing_data = device_sharing(node_id)
        if device_sharing_data:
            url_lst = find_url(device_sharing_data)
            if len(url_lst) > 0:
                return url_lst[0]
            else:
                device_sharing_data = device_sharing(node_id, url_avail = False)
                if device_sharing_data:
                    url_lst = find_url(device_sharing_data)
                    return url_lst[0]
                else: 
                    return []
        else:
            return []
    else:
        return []
    
    
def getNodeID(serial_number):
    try:
        collection = db["meshcentral"]
        data = collection.find({"hardware.identifiers.bios_serial" : serial_number})
        data = list(data)
        if data:
            node_id = data[0].get("_id", None)
            return node_id[2:]
        else:
            return 0
    except Exception as e:
        print("Exception in getNodeID",e)
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
        return []

        
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
        query_2 = collection.find({'org_id' : org_id},{'org_id' : 1,'_id': 0})
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
                command = f'node meshctrl  AgentDownload --id {group_id} --type {architecture_id} --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234" '
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
        
def processForUrl(node_info):
    '''
        return the Url based on the serial number. if serial number present in db , it will return the respective url or else
        the url will be generated only if the serial number is valid and return url also update the generated url to its respective
        serial number. 
    '''
    try:
        collection = db["org_id"]
        query = collection.find({'org_id' : node_info.organization},{'org_id' : 1,'_id': 0})
        data = list(query)
        generate_url = 0
        if len(data) > 0:
            connection_params = collection.find({'org_id' : node_info.organization},{'connection_params':1, '_id':0})
            connection_params = list(connection_params)[0] 
            if connection_params.get('connection_params'):
                con_objs  = connection_params.get('connection_params')
                for obj in con_objs:
                    url = obj.get(node_info.serial_number,None)
                if url is not None:
                    response =  url
                else:
                    generate_url = 1
            else:
                generate_url = 1
            if generate_url == 1:
                url = fetchUrl(node_info.serial_number)
                if url:
                    filter_query = {"org_id": node_info.organization}
                    update_data = {
                        'serial_number' : node_info.serial_number,
                        'url' : url
                    }                
                    update_query = {"$push": {"connection_params": {update_data["serial_number"]: update_data["url"]}}}
                    update_result = collection.update_one(filter_query, update_query)
                    if update_result.modified_count > 0:
                        print("Created the URL and updated Successfully.")
                    else:
                        print("Created the url but cannot update the db.")
                    response = url
                else:
                    return HTTPException(detail=f"Cannot fetch the URL for this serial number {node_info.serial_number}.", status_code=status.HTTP_400_BAD_REQUEST)
            return response
        else:
            return HTTPException(detail=f"Organization ID is Not Valid : {node_info.organization}",status_code=status.HTTP_400_BAD_REQUEST)         
    except Exception as e:
        print("Exception in processurl",e) 
        return HTTPException(detail=f"Exception in getting the URL.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)  
                
