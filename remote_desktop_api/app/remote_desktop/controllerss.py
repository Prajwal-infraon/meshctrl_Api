import subprocess
from pymongo import MongoClient
import re
from fastapi.responses import FileResponse
import json

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
        query = collection.find({"org_id":org_id})
        raw_query = list(query)
        if len(raw_query):   
            print("true >>>")
            group_id = raw_query[0].get("_id","")
            group_id = group_id[6:]
            print(group_id)
        if not group_id:
            try:
                command= f'node meshctrl adddevicegroup --name \'{org_id}\' --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.stderr:
                    group_id = ""
                else:
                    group_id = result.stdout[9:]
                    group_id = group_id.strip()
                    try:
                        add_group = collection.insert_one({"org_id":org_id,"mesh_id":group_id})
                    except :
                        print("error")
                    
            except subprocess.CalledProcessError as e:
                print("Error running the command:",e.stderr)
            command = f'node meshctrl  AgentDownload --id {group_id} --type {architecture_id} --url wss://127.0.0.1 --loginuser "demo" --loginpass "1234"'
            print(command)
            try:
                result_1 = subprocess.run(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                if not result_1.stderr:
                    res = result_1.stdout
                else:
                    print("/////",result_1)
                return res 
            except subprocess.CalledProcessError as e:
                print("Error running the command:",e.stderr)
        
    except Exception as msg:
        print("2345",msg)
        
        
        
def cmd_call():
    try:
        command = 'D:/remote_desktop_api/ InfraonRemoteAgent32-12345678.exe --fullinstall'
        print(command)
        result = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        print(result)
        return result
    except subprocess.CalledProcessError as e :
        print(e)

    