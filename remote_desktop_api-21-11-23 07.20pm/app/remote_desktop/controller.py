import subprocess
from pymongo import MongoClient
import re
from fastapi.responses import FileResponse,Response
import json
from fastapi import HTTPException, status
import os,shutil
from pathlib import Path
import pathlib
import hashlib
import urllib.parse


js_file = "meshctrl.js"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["meshcentral"]
collection = db["meshcentral"]

def fetchUrl(serial_number,organization):
    node_id = getNodeID(serial_number, organization)
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
    
    
def getNodeID(serial_number,organization):
    try:
        collection = db["meshcentral"]
        data = collection.find({"hardware.identifiers.bios_serial" : serial_number})
        data = list(data)
        if data:
            node_id = data[0].get("_id", None)
            data2 = collection.find({"_id" :node_id[2:]},{'meshid':1,'_id':0})
            print(list(data2))
            org_col = db["org_id"]
            mesh_id = org_col.find({'org_id': organization},{'mesh_id':1,'_id':0})
            print(list(mesh_id))
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


def getAgentexe(org_info):
    group_id = ""
    collection = db["org_id"]
    file_name_map = {
        3 : "InfraonRemoteAgent32",
        4 : "InfraonRemoteAgent64",
        5 : "InfraonRemoteAgentarm64" 
    }
    try:
        query_2 = collection.find({'org_id' : org_info.org_id},{'org_id' : 1,'_id': 0})
        raw_query_res = list(query_2)
        if not raw_query_res: 
            command= f'node meshctrl adddevicegroup --name \'{org_info.org_id}\' --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
            else:
                group_id = result.stdout[9:]
                group_id = group_id.strip()
                collection.insert_one({"org_id":org_info.org_id,"mesh_id":group_id})
                command = f'node meshctrl  AgentDownload --id {group_id} --type {org_info.architecture_id} --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234" '
                result_1 = subprocess.run(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                if not result_1.stderr:
                    res = result_1.stdout
                    file_name = f"{file_name_map.get(org_info.architecture_id)}-{org_info.org_id}.exe"
                    current_directory = os.getcwd()
                    file_path = os.path.join(current_directory, file_name)
                    if os.path.exists(file_path):
                        destination_folder = os.path.join(current_directory, "Agents") 
                    if not os.path.exists(destination_folder):
                        os.makedirs(destination_folder)
                    shutil.move(file_path, destination_folder)
                    file_path = os.path.join(destination_folder, file_name)
                    if os.path.exists(file_path):
                        try :
                            base_url = 'http://127.0.0.1:8000/get-file?file_name='
                            file_name = encode_file_name(file_name)
                            http_url = base_url + file_name
                            print(http_url)
                        except Exception as e:
                            return e
                       
                        return http_url
                    else:
                        return {"error": "File not found"}
                else:
                    res =None
                    return HTTPException(detail=f"Error in executing the Command: {command}", status_code=status.HTTP_404_NOT_FOUND)
        else:
            return HTTPException(detail=f"org_id : {org_info.org_id} Already exist.", status_code=status.HTTP_403_FORBIDDEN)
    except Exception as msg:
        print(msg)
        return HTTPException(detail="Exception in downloading Agent", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


import base64

def encode_file_name(file_name):
    encoded_bytes = base64.urlsafe_b64encode(file_name.encode())
    encoded_file_name = encoded_bytes.decode()
    return encoded_file_name

def decode_file_name(encoded_file_name):
    decoded_bytes = base64.urlsafe_b64decode(encoded_file_name)
    decoded_file_name = decoded_bytes.decode()
    return decoded_file_name    
        
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
            query_key = f"connection_params.{node_info.serial_number}"
            url = collection.find_one(
                {'org_id': node_info.organization, query_key: {'$exists': True}}, 
                {query_key: 1, '_id': 0}
            )
            if url is not None:
                url_ = url['connection_params'][node_info.  serial_number]
                response = url_
            else:
                generate_url = 1
            if generate_url == 1:
                url = fetchUrl(node_info.serial_number, node_info.organization)
                if url:
                    filter_query = {"org_id": node_info.organization}
                    update_query = {node_info.serial_number: url} 
                    connection_params = {"connection_params" : update_query} # Get the update query data or an empty dictionary if not found
                    update_result = collection.update_one(filter_query, {"$set": connection_params})
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
                
