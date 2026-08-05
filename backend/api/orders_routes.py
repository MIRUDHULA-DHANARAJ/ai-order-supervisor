# backend/api/orders_route.py
from fastapi import APIRouter, HTTPException
from schemas.order import SpawnRunSchema, SignalPayloadSchema, InstructionUpdateSchema
from services.temporal_service import temporal_service
from workflows.order_supervisor import OrderSupervisorWorkflow
from db.session import SessionLocal
from models.order import OrderRunModel, TimelineEventModel

router = APIRouter(prefix="/api/runs", tags=["runs"])

@router.get("")
async def get_all_runs_history():
    db = SessionLocal()
    try:
        return db.query(OrderRunModel).order_by(OrderRunModel.created_at.desc()).all()
    finally:
        db.close()

@router.get("/{run_id}")
async def get_single_run_details(run_id: str):
    db = SessionLocal()
    try:
        run = db.query(OrderRunModel).filter(OrderRunModel.id == run_id).first()
        events = db.query(TimelineEventModel).filter(TimelineEventModel.run_id == run_id).order_by(TimelineEventModel.created_at.asc()).all()
        return {"run": run, "timeline": events}
    finally:
        db.close()

@router.post("")
async def initialize_order_supervisor(payload: SpawnRunSchema):
    db = SessionLocal()
    try:
        existing_run = db.query(OrderRunModel).filter(OrderRunModel.id == payload.order_id).first()
        if existing_run:
            return {"status": "ALREADY_ACTIVE", "run_id": payload.order_id}

        new_run = OrderRunModel(id=payload.order_id, template_id="tmpl_default", status="RUNNING")
        db.add(new_run)
        db.commit()
        
        client = await temporal_service.get_client()
        await client.start_workflow(
            OrderSupervisorWorkflow.run,
            id=payload.order_id,
            args=[payload.order_id, payload.initial_context],
            task_queue="order-supervisor-tasks"
        )
        return {"status": "LAUNCHED", "run_id": payload.order_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/{run_id}/events")
async def inject_lifecycle_signal(run_id: str, payload: SignalPayloadSchema):
    try:
        client = await temporal_service.get_client()
        handle = client.get_workflow_handle(run_id)
        await handle.signal(OrderSupervisorWorkflow.process_signal_event, {"type": payload.event_type, "payload": payload.data})
        return {"status": "SIGNAL_PROCESSED"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{run_id}/instructions")
async def append_runtime_instructions(run_id: str, payload: InstructionUpdateSchema):
    try:
        client = await temporal_service.get_client()
        handle = client.get_workflow_handle(run_id)
        await handle.signal(OrderSupervisorWorkflow.inject_additional_instructions, payload.instructions)
        return {"status": "INSTRUCTIONS_UPDATED"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{run_id}/interrupt")
async def pause_active_workflow(run_id: str):
    db = SessionLocal()
    try:
        client = await temporal_service.get_client()
        handle = client.get_workflow_handle(run_id)
        await handle.signal(OrderSupervisorWorkflow.pause_workflow)
        
        run = db.query(OrderRunModel).filter(OrderRunModel.id == run_id).first()
        if run:
            run.status = "INTERRUPTED"
            db.commit()
        return {"status": "INTERRUPTED"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/{run_id}/resume")
async def resume_paused_workflow(run_id: str):
    db = SessionLocal()
    try:
        client = await temporal_service.get_client()
        handle = client.get_workflow_handle(run_id)
        await handle.signal(OrderSupervisorWorkflow.resume_workflow)
        
        run = db.query(OrderRunModel).filter(OrderRunModel.id == run_id).first()
        if run:
            run.status = "RUNNING"
            db.commit()
        return {"status": "RUNNING"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/{run_id}/terminate")
async def terminate_workflow_run(run_id: str):
    db = SessionLocal()
    try:
        client = await temporal_service.get_client()
        handle = client.get_workflow_handle(run_id)
        await handle.terminate(reason="Manual human terminal override.")
        
        run = db.query(OrderRunModel).filter(OrderRunModel.id == run_id).first()
        if run:
            run.status = "TERMINATED"
            db.commit()
        return {"status": "TERMINATED"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
