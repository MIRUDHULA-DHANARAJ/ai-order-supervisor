# backend/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.orders_routes import router as order_router
from services.temporal_service import temporal_service
from workflows.order_supervisor import OrderSupervisorWorkflow
from activities.order_activities import (
    classify_incoming_event_activity,
    execute_agent_reasoning_activity,
    compile_final_summary_activity
)
from temporalio.worker import Worker
from db.session import engine, Base

# Build database tables automatically on application startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sagepilot AI - Simple Order Supervisor POC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order_router)

async def launch_temporal_worker():
    "Runs a worker process directly inside the FastAPI main event loop."
    try:
        client = await temporal_service.get_client()
        worker = Worker(
            client,
            task_queue="order-supervisor-tasks",
            workflows=[OrderSupervisorWorkflow],
            activities=[
                classify_incoming_event_activity,
                execute_agent_reasoning_activity,
                compile_final_summary_activity
            ]
        )
        print("🚀 Temporal worker attached and listening on task queue...")
        await worker.run()
    except Exception as e:
        print(f"Temporal worker failed to initialize: {e}")

@app.on_event("startup")
async def app_startup_handler():
    asyncio.create_task(launch_temporal_worker())
