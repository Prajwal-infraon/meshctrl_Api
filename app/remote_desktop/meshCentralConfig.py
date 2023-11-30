import os

MONGO_URL = "mongodb://localhost:27017"
MESH_CENTRAL_COLLECTION = "meshcentral"
INFRAON_COLLECTION = "org_id"
WSS_URL = "wss://52.248.44.93"
MESH_CENTRAL_USERNAME = "demo"
MESH_CENTRAL_PASSWORD = "1234"
CWD = os.getcwd()
DOWNLOAD_BASE_URL = 'http://52.248.44.93:8000/get-file?file_name='
FILE_NAME_MAP = {
        3: "InfraonRemoteAgent32",
        4: "InfraonRemoteAgent64",
        5: "InfraonRemoteagent",
        43: "InfraonRemoteAgentarm64",
    }