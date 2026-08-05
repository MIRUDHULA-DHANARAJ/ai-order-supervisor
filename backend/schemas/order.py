# backend/schemas/order.py
from pydantic import BaseModel
from typing import Dict

class SpawnRunSchema(BaseModel):
    order_id: str
    initial_context: Dict

class SignalPayloadSchema(BaseModel):
    event_type: str
    data: Dict

class InstructionUpdateSchema(BaseModel):
    instructions: str
