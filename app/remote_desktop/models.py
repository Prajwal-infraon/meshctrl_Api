
from pydantic import BaseModel
 
 
class NodeInfoRequest(BaseModel):
    organization: str
    serial_number: str

class AgentExeRequest(BaseModel):
    organization: str
    architecture_id: int