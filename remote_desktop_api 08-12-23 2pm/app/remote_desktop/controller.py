from .utility import *
# from .models import powerstatus
def processForUrl(node_info):
    """
    Function to get the connection url for the remote connection
    :param node_info : serial_number and organization id of the asset
    :return response : It contains the url and status message
    """
    url_lst = []
    node_id = ""
    url = ""
    status = 0
    try:
        logger.info(
            "Enter into processForUrl function in controller for %s" % (node_info)
        )
        collection = db[INFRAON_COLLECTION]
        # check if the organization is already exists in the mesh_central DB
        raw_query = collection.find({"org_id": node_info.organization})
        data = list(raw_query)
        if data:
            group_id = data[0].get("mesh_id","")
            node_id = getNodeID(node_info)
            device_id = node_id[6:]
            # check the power status of the device (offline or online)
            status = powcheck(group_id,device_id)
            power_status =status[1]
            online_device_node_id = status[0]
            node_id = online_device_node_id[6:]
            device_duplicated = status[-1]
            if power_status == 1:
                #checks the device duplication in DB if it's present fetch the ulr from DB
                if device_duplicated == True:
                    raw_query_data = f"connection_params.{node_info.serial_number}.{node_id}"
                    query_data = collection.find_one({raw_query_data: {'$exists': True}}, {'_id': 0,raw_query_data:1})
                    # if both device and url is preset in meshcentral DB it will return the url
                    if query_data:
                        url = query_data.get('connection_params').get(node_info.serial_number).get(node_id)
                        response  = url
                    #if device is present but url is not present it will generate the url(generate_url)
                    else:
                        generate_url = True
                        logger.error(f"Device exist with nodeid {node_id} but the data is not present in DB.")
                #generate the device_sharing url and update to meshcentral MongoDB if not in DB
                if device_duplicated == False or generate_url == True:
                    #check data in MC DB
                    raw_query_data = f"connection_params.{node_info.serial_number}.{node_id}"
                    query_data = collection.find_one({raw_query_data: {'$exists': True}}, {'_id': 0,raw_query_data:1})
                    #if url present it returns the url
                    if query_data:
                        url = query_data.get('connection_params').get(node_info.serial_number).get(node_id)
                        response  = {"data": url, "message": "proceed_remote_connection"}
                    #if its not present not there will generate the url
                    else:
                        logger.debug("Generate connection string from mesh central")
                        node_id = online_device_node_id[6:]
                        if node_id:
                            url_lst = device_sharing(node_id, url_avail=False)
                        if url_lst:
                            url = url_lst[0]
                        if url:
                            filter_query = {"org_id": node_info.organization}
                            connection_params = {
                                "connection_params.%s" % (node_info.serial_number): {
                                    node_id : url
                                }
                            }
                            update_result = collection.update_one(
                                filter_query, {"$set": connection_params}
                            )
                            if update_result.modified_count > 0:
                                response = {"data": url, "message": "proceed_remote_connection"}
                        # if no url found, prompt user ti download mesh_central agent
                            else:
                                response = {"data": "", "message": "agent_not_found"}
                        # if the organization is not found in existing data, prompt user to download mesh_central agent
                        else:
                            response = {"data": "", "message": "agent_not_found"}
                    logger.info(
                        "Exit processForUrl function in controller with response %s" % (response)
                    )
            else:
                response = {"data": "", "message": "Device not Powered on"}
        else:
            response = {"data": "", "message": "org_id  not present"}
    except Exception as exp:
        response = {"data": "", "message": "download_error"}
        logger.exception(
            "Exception in processForUrl %s with type %s" % (exp, type(exp))
        )
    return response

def getAgentexe(exe_info):
    group_id = ""
    collection = db[INFRAON_COLLECTION]
    destination_folder = ""
    try:
        logger.info(
            "Enter into getAgentexe function in controller with %s" % (exe_info)
        )
        query = collection.find({"org_id": exe_info.organization})
        data = list(query)
        http_url = ""
        file_name = ""
        # if the organization is not present in the mesh_central db, create a new group from organization id
        if not data:
            logger.debug("Create mesh since organization is not found in DB")
            command = f"node meshctrl adddevicegroup --name '{exe_info.organization}' --features 1 --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} "
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if not result.stderr:
                response = result.stderr
                pattern = r'Unable to connect to wss://52.248.44.93/control.ashx'
                if not re.search(pattern, response):
                    group_id = result.stdout[9:]
                    group_id = group_id.strip()
                    # update the collection with mapped data
                    collection.insert_one(
                        {"org_id": exe_info.organization, "mesh_id": group_id}
                    )
                else:
                    logger.error("Mesh central server not turned on !!!")
                if group_id:
                    # generate exe based on group and architecture type
                    command = f"node meshctrl  AgentDownload --id {group_id} --type {exe_info.architecture_id} --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} "
                    result_1 = subprocess.run(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if not result_1.stderr:
                        res = result_1.stdout
                        # construct file_name
                        file_name = f"{FILE_NAME_MAP.get(exe_info.architecture_id, 3)}-{exe_info.organization}.exe"
                        file_path = os.path.join(CWD, file_name)
                        if os.path.exists(file_path):
                            destination_folder = os.path.join(CWD, "Agents")            
                        if not os.path.exists(destination_folder):
                            os.makedirs(destination_folder)
                        # move the file to the Agents folder after generating
                        if os.path.exists(file_path):
                            try:
                                shutil.move(file_path, destination_folder)
                            except Exception as e:
                                logger.error("File already exists in agents folder")
                                os.remove(file_path)

        # if organization is already exists in the mesh_central db
        else:
            logger.debug("Organization mapping is found in DB")
            group_id = data[0].get("mesh_id")
            if group_id:
                # construct the file name based on the available data
                file_name = f"{FILE_NAME_MAP.get(exe_info.architecture_id, 3)}-{exe_info.organization}.exe"
                destination_folder = os.path.join(CWD, "Agents")
                file_path = os.path.join(destination_folder, file_name)
                # if file doesn't exists then generate a exe based on architecture and move it to Agents folder
                if not os.path.exists(file_path):
                    logger.debug("Generating exe since no existing exe is found")
                    command = f"node meshctrl  AgentDownload --id {group_id} --type {exe_info.architecture_id} --url {WSS_URL} --loginuser {MESH_CENTRAL_USERNAME} --loginpass {MESH_CENTRAL_PASSWORD} "
                    result_1 = subprocess.run(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if not result_1.stderr:
                        file_path = os.path.join(CWD, file_name)
                        if os.path.exists(file_path):
                            shutil.move(file_path, destination_folder)
                else:
                    logger.debug("no need to generate new exe,  file already exists")
        if file_name and group_id:
            file_name = encode_file_name(file_name)
            # construct http url for serving the agent file
            http_url = DOWNLOAD_BASE_URL + file_name
        logger.info(
            "Exit from getAgentexe function in controller with url %s" % (http_url)
        )
        return http_url
    except Exception as msg:
        logger.exception(
            "Exception in getAgentexe in controller for %s with type %s"
            % (msg, type(msg))
        )
        return HTTPException(
            detail="Exception in downloading Agent",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

