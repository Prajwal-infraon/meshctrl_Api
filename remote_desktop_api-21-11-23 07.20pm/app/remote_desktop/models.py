
from pydantic import BaseModel
 
 
class NodeInfoRequest(BaseModel):
    organization: str
    serial_number: str
 
class getagentexe(BaseModel):
    org_id:str
    architecture_id:int