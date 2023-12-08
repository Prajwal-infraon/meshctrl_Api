import base64
from .logmanager import *
from .meshCentralConfig import *
import subprocess
from pymongo import MongoClient
import re
from fastapi import HTTPException, status
import os
import shutil
from .meshCentralConfig import *
# from .models import powerstatus

logger,_ = configure_loggers()
js_file = "meshctrl.js"

mongo_client = MongoClient(MONGO_URL)
db = mongo_client[MESH_CENTRAL_COLLECTION]
collection = db[MESH_CENTRAL_COLLECTION]


def encode_file_name(file_name):
    """
    Function to encode the agent file name in the url
    :param file_name : file name of the exe
    :return encoded_file_namee : encoded file name
    """
    encoded_file_name = ""
    try:
        logger.info(
            "Enter into encode_file_name function in controller with %s" % (file_name)
        )
        encoded_bytes = base64.urlsafe_b64encode(file_name.encode())
        encoded_file_name = encoded_bytes.decode()
        logger.info(
            "Exit from encode_file_name function in controller with %s"
            % (encoded_file_name)
        )
    except Exception as exp:
        logger.exception(
            "Exception in encode_file_name function in controller with %s for type %s"
            % (exp, type(exp))
        )
    return encoded_file_name


def decode_file_name(encoded_file_name):
    """
    Function to decode the file name in the url
    :param encoded_file_name
    :return decoded_file_name
    """
    decoded_file_name = ""
    try:
        logger.info(
            "Enter into decode_file_name function in controller with %s"
            % (encoded_file_name)
        )
        decoded_bytes = base64.urlsafe_b64decode(encoded_file_name)
        decoded_file_name = decoded_bytes.decode()
        logger.info(
            "Exit from decode_file_name function in controller with %s"
            % (decoded_file_name)
        )
    except Exception as exp:
        logger.exception(
            "Exception in encode_file_name function in controller with %s for type %s"
            % (exp, type(exp))
        )
    return decoded_file_name

def getNodeID(node_info):
    """
    Function to get the node_id of the remote asset from the serial number
    :param serial_number : serial number of the asset
    :return node_id
    """
    node_id: str = ""
    data: list = []
    try:
        logger.info(
            "Enter into getNodeID function in controller with %s" % (node_info)
        )
        raw_data = collection.find(
            {
                "$or": [
                    {"hardware.identifiers.bios_serial": node_info.serial_number},
                    {"hardware.identifiers.board_serial": node_info.serial_number},
                ]
            }
        )  # "NHQ87SI001020008EF3400"
        data = list(raw_data)
        if data:
            node_id = data[0].get("_id", "")
            node_id = node_id[2:]
        logger.info("Exit from getNodeID function with %s" % (node_id))
    except Exception as exp:
        logger.exception(
            "Exception in getNodeID for %s with type %s" % (exp, type(exp))
        )
    return node_id


def device_sharing(node_id, url_avail=True):
    """
    Function to get the connection url from the node_id
    :param node_id: Node ID of the remote asset
    :param url_avail : Boolean value denoting availability of any existing connection url
    """
    url_lst: list = []
    urls: list = []
    try:
        logger.info(
            "Enter into device_sharing function in controller with node_id %s"
            % (node_id)
        )
        # if any connection url available already in the node
        if url_avail == True:
            command = f"node meshctrl DeviceSharing --id {node_id} --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} "
        # generate connection url for the node
        elif url_avail == False:
            command = f"node meshctrl DeviceSharing --id {node_id} --add RemoteAccess --type desktop --consent prompt  --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} "
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        if not result.stderr:
            urls = re.findall(r"https://[^\s]+", result.stdout)
            for url in urls:
                url_lst.append(url[:-1])
        logger.info("Exit from device_sharing with url %s" % (url_lst))
    except subprocess.CalledProcessError as e:
        logger.exception(
            "Exception in device_sharing function for %s with type %s" % (e, type(e))
        )
    return url_lst


def powcheck(group_id,device_id):
    """
    Function to checks the device status (offline or online)
    group_id: to check the perticular group device 
    device_id : to check the perticular device status
    
    """
    response = ["",-1]
    try:
        command = f"node meshctrl listdevices --id {group_id} --filter [{device_id}] --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} --json"
        result_1 = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        ress1 =result_1.stdout
        #converting data to json and fetching required information
        import json
        ress1 = json.loads(ress1)
        
        #defining the status based on the value
        if len(ress1)>1:
            device_duplicated = True
        else: 
            device_duplicated = False
        if ress1 != []:
            for node in ress1:
                if node.get('pwr', None):
                    response =  [node.get("_id",""), node.get("pwr","")]
        logger.info("Data of powered node_id %s" %(response))
    except subprocess.CalledProcessError as e:
        logger.exception(">>>>>>>>>>>>>>>check power<<<<<<<<<<<<<< %s" %(e,type(e)))
    response.append(device_duplicated)
    return response