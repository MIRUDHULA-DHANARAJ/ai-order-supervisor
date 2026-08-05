from pydantic import BaseModel


class CreateRunRequest(BaseModel):
    order_id: str
    supervisor_id: int
class CreateRunResponse(BaseModel):
    workflow_id: str
    status: str
class EventRequest(BaseModel):
    type: str