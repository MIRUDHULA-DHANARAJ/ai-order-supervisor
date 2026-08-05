# backend/models/order.py
import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, JSON, Text
from db.session import Base

class SupervisorTemplateModel(Base):
    __tablename__ = "supervisor_templates"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    base_instruction = Column(Text, nullable=False)
    model_choice = Column(String, default="llama-3.3-70b-versatile")

class OrderRunModel(Base):
    __tablename__ = "order_runs"
    id = Column(String, primary_key=True)  # Maps 1:1 to Temporal Workflow ID
    template_id = Column(String, default="default_template")
    status = Column(String, default="RUNNING")  # RUNNING, PAUSED, COMPLETED, TERMINATED
    memory_summary = Column(Text, default="Order initialized.")
    additional_instructions = Column(Text, default="")
    final_output = Column(JSON, nullable=True)  # Summaries, learnings, recommendations
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TimelineEventModel(Base):
    __tablename__ = "timeline_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    run_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    agent_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
