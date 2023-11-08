import subprocess
from pymongo import MongoClient
import re
import json

js_file = "meshctrl.js"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["meshcentral"]
collection = db["meshcentral"]

def processForUrl(serial_number):
    node_id = getNodeID(serial_number)
    print(node_id)
    device_sharing_data = device_sharing(node_id)
    print(device_sharing_data)
    url_lst = find_url(device_sharing_data)
    if len(url_lst) > 0:
        return url_lst[0]
    else:
        device_sharing_data = device_sharing(node_id, url_avail = False)
        url_lst = find_url(device_sharing_data)
        print(url_lst)
        if url_lst:
            return url_lst[0]
    
    
def getNodeID(serial_number):
    data = collection.find({"$or":[{"hardware.identifiers.bios_serial" : serial_number}, {"hardware.identifiers.board_serial":serial_number}]})     #"NHQ87SI001020008EF3400"
    raw_data = list(data)
    if raw_data:
        node_id = raw_data[0].get("_id", None)
        return node_id[2:]
    else:
        return 0
    
def device_sharing(node_id, url_avail = True):
    if url_avail == True:
        command = f'node meshctrl DeviceSharing --id {node_id} --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234"'
    elif url_avail == False:
        command = f'node meshctrl DeviceSharing --id {node_id} --add infraon_desktop --type desktop,terminal --consent prompt  --url wss://52.248.44.93 --loginuser "demo" --loginpass "1234"'
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