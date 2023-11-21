import subprocess
from pymongo import MongoClient
import re
from fastapi.responses import FileResponse
import json
from fastapi import HTTPException, status
import os
import shutil

js_file = "meshctrl.js"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["meshcentral"]
collection = db["meshcentral"]



def processForUrl(node_info):
    '''
        return the Url based on the serial number. if serial number present in db , it will return the respective url or else
        the url will be generated only if the serial number is valid and return url also update the generated url to its respective
        serial number. 
    '''
    url_lst = []
    node_id = ""
    url = ""
    try:
        collection = db["org_id"]
        raw_query = collection.find({"org_id" : node_info.organization})
        data = list(raw_query)
        if data:
            print(data)
            for orgs in data:
                if orgs.get("connection_params"):
                    node_details = orgs.get("connection_params")
                    url = node_details.get(node_info.serial_number, "")
            if url:
                response = {"data": url, "message": "proceed_remote_connection"}
            else:
                node_id = getNodeID(node_info)
                # print("node_id >>>", node_id)
                if node_id:
                    url_lst = device_sharing(node_id, url_avail = False)
                # print("url >>>", url_lst)
                if url_lst:
                    url =  url_lst[0]
                if url :
                    filter_query = {"org_id": node_info.organization}
                    update_query = {node_info.serial_number: url} 
                    connection_params = {"connection_params.%s"%(node_info.serial_number) : url} # Get the update query data or an empty dictionary if not found
                    update_result = collection.update_one(filter_query, {"$set": connection_params})
                    if update_result.modified_count > 0:
                        response = {"data": url, "message": "proceed_remote_connection"}
                else:
                    response = { "data": "", "message": "agent_not_found"}
        else:
            response = {"data": "", "message": "agent_not_found"}

    except Exception as exp:
        response =  {"data": "", "message": "download_error"}
    return response
        
def getNodeID(node_info):
    """
    Function to get the node_id of the remote asset from the serial number
    :param serial_number : serial number of the asset
    :return node_id
    """
    node_id : str = ""
    data : list = []
    try:
        raw_data = collection.find({"$or":[{"hardware.identifiers.bios_serial" : node_info.serial_number}, {"hardware.identifiers.board_serial":node_info.serial_number}]})     #"NHQ87SI001020008EF3400"
        data = list(raw_data)
        if data:
            node_id = data[0].get("_id", "")
            node_id = node_id[2:]
    except Exception as exp:
        node_id = ""
    return node_id
    
def device_sharing(node_id, url_avail = True):
    """
    Function to get the connection url from the node_id
    :param node_id: Node ID of the remote asset
    :param url_avail : Boolean value denoting availability of any existing connection url
    """
    url_lst : list = []
    urls : list = []
    try:
        if url_avail == True:
            command = f'node meshctrl DeviceSharing --id {node_id} --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234"'
        elif url_avail == False:
            command = f'node meshctrl DeviceSharing --id {node_id} --add infraon_desktop --type desktop --consent prompt  --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234"'
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print(result)
        if not result.stderr:
            urls = re.findall(r'https://[^\s]+',result.stdout)
            for url in urls:
                url_lst.append(url[:-1])
    except subprocess.CalledProcessError as e:
        url_lst = []
    return url_lst
    
def getAgentexe(exe_info):
    group_id = ""
    collection = db["org_id"]
    file_name_map = {
        3 : "InfraonRemoteAgent32",
        4 : "InfraonRemoteAgent64",
        5 : "InfraonRemoteAgentarm64" 
    }
    try:
        query = collection.find({'org_id' : exe_info.organization},{'org_id' : 1,'_id': 0})
        data = list(query)
        if not data: 
            command= f'node meshctrl adddevicegroup --name \'{exe_info.organization}\' --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234"'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
            else:
                group_id = result.stdout[9:]
                group_id = group_id.strip()
                collection.insert_one({"org_id":exe_info.organization,"mesh_id":group_id})
                command = f'node meshctrl  AgentDownload --id {group_id} --type {exe_info.architecture_id} --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234" '
                result_1 = subprocess.run(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                if not result_1.stderr:
                    res = result_1.stdout
                    file_name = f"{file_name_map.get(exe_info.architecture_id, 3)}-{exe_info.organization}.exe"
                    current_directory = os.getcwd()
                    print(current_directory)
                    file_path = os.path.join(current_directory, file_name)
                    print(file_path)
                    if os.path.exists(file_path):
                        destination_folder = os.path.join(current_directory, "Agents") 
                    print("destination >>>", destination_folder)   
                    if not os.path.exists(destination_folder):
                        os.makedirs(destination_folder)
                    shutil.move(file_path, destination_folder)
                    file_path = os.path.join(destination_folder, file_name)
                    if os.path.exists(file_path):
                        return {"name": file_name, "path": file_path}
                    else:
                        return {"error": "File not found"}
                else:
                    res = None
                    return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
            return res 
        else:
            return HTTPException(detail=f"org_id : {exe_info.organization} Already exist.", status_code=status.HTTP_403_FORBIDDEN) #send the exe
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
        
