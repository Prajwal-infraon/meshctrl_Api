"""
    File            :   API Controller
    Package         :   Organization
    Description     :   Used for execute the mesh central integration with inventory agent
    Project Name    :   Infinity-SAAS
    Created by Prajwal Kumar on 6th Nov 2023
"""
__author__ = 'Prajwal Kumar'
__version__ = "0.1"

import subprocess
from pymongo import MongoClient
import re
import json

js_file = "meshctrl.js"

mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["meshcentral"]
collection = db["meshcentral"]


def get_connection_url(asset_data: dict):
    """
    Function to get the connection url for the remote desktop
    :param serial_number : Serial number of the asset
    :return connection url
    """
    node_id : str = ""
    connection_url : str = ""
    url_lst : list = []
    try:
        if asset_data:
            serial_number : str = asset_data.get("serial_number")
            node_id = getNodeID(serial_number)
            if node_id:
                url_lst = device_sharing(node_id)
                if url_lst:
                    connection_url = url_lst[0]
                else:
                    url_lst = device_sharing(node_id, url_avail = False)
                    connection_url = url_lst[0]
    except Exception as exp:
        connection_url = ""
    return connection_url
 
def getNodeID(serial_number):
    """
    Function to get the node_id of the remote asset from the serial number
    :param serial_number : serial number of the asset
    :return node_id
    """
    raw_node_id : str = ""
    node_id : str = ""
    data : list = []
    try:
        data = collection.find({"$or":[{"hardware.identifiers.bios_serial" : serial_number}, {"hardware.identifiers.board_serial":serial_number}]})     #"NHQ87SI001020008EF3400"
        if data:
            raw_node_id = data[0].get("_id", None)
            node_id = raw_node_id[2:]
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
        if result:
            urls = re.findall(r'https://[^\s]+',result.stdout)
            for url in urls:
                url_lst.append(url[:-1])
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)
    return url_lst



