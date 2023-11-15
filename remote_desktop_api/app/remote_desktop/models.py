
from pydantic import BaseModel
 
 
class NodeInfoRequest(BaseModel):
    organization: str
    serial_number: str
 
 