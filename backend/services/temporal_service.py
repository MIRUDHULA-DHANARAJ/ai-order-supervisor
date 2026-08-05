# backend/services/temporal_service.py
import os
from temporalio.client import Client

class TemporalService:
    def __init__(self):
        self.client = None

    async def get_client(self) -> Client:
        if not self.client:
            host = os.getenv("TEMPORAL_HOST", "localhost:7233")
            self.client = await Client.connect(host)
        return self.client

temporal_service = TemporalService()
