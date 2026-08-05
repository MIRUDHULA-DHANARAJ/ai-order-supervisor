# backend/activities/order_activities.py
import json
from temporalio import activity
from db.session import SessionLocal
from models.order import OrderRunModel, TimelineEventModel
from agents.supervisor_agent import OrderSupervisorAgent

agent = OrderSupervisorAgent()

@activity.defn
async def classify_incoming_event_activity(event: dict) -> bool:
    return agent.classify_event(event.get("type", ""))

@activity.defn
async def execute_agent_reasoning_activity(ctx: dict) -> str:
    order_id = ctx["order_id"]
    trigger = ctx["trigger"]
    events = ctx["events"]
    instructions = ctx["instructions"]
    
    db = SessionLocal()
    try:
        run_record = db.query(OrderRunModel).filter(OrderRunModel.id == order_id).first()
        history = run_record.memory_summary if run_record else ""
        
        agent_output = agent.execute_reasoning_cycle(trigger, events, instructions, history)
        
        # Log the specific business action as a persistent activity record
        action_name = agent_output.get("action", "create_internal_note")
        action_text = agent_output.get("parameters", {}).get("text", "Processed standard cycle.")
        executed_activity_record = f"Action: [{action_name}] -> {action_text}"

        if run_record:
            run_record.memory_summary = agent_output.get("compact_memory", history)
            if instructions:
                run_record.additional_instructions = instructions
        
        new_event = TimelineEventModel(
            run_id=order_id,
            event_type=trigger,
            payload={"events_evaluated": events, "action_taken": executed_activity_record},
            agent_action=agent_output.get("thought", "Analyzed metrics.")
        )
        db.add(new_event)
        db.commit()
        return json.dumps(agent_output)
    finally:
        db.close()

@activity.defn
async def compile_final_summary_activity(ctx: dict) -> dict:
    order_id = ctx["order_id"]
    instructions = ctx["instructions"]
    db = SessionLocal()
    try:
        run_record = db.query(OrderRunModel).filter(OrderRunModel.id == order_id).first()
        history = run_record.memory_summary if run_record else ""
        
        final_report = agent.compile_final_report(history, instructions)
        
        if run_record:
            run_record.status = "COMPLETED"
            run_record.final_output = final_report
            db.commit()
        return final_report
    finally:
        db.close()
