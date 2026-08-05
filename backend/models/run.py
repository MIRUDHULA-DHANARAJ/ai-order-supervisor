from pydantic import BaseModel


class CreateRunRequest(BaseModel):
    order_id: str
    supervisor_id: int