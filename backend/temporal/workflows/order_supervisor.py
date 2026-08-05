# backend/workflows/order_supervisor.py
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.order_activities import (
        classify_incoming_event_activity,
        execute_agent_reasoning_activity,
        compile_final_summary_activity
    )

@workflow.defn
class OrderSupervisorWorkflow:
    def __init__(self) -> None:
        self.events_queue: list = []
        self.runtime_instructions: str = ""
        self.is_completed: bool = False
        self.should_wake_up: bool = False

    @workflow.signal
    async def process_signal_event(self, event: dict) -> None:
        "Fires instantly whenever an event hits our web server endpoints."
        self.events_queue.append(event)
        
        # Run the lightweight classifier activity to check priority
        is_critical = await workflow.execute_activity(
            classify_incoming_event_activity,
            event,
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # Wake the workflow if it's high priority or a completion event
        if is_critical or event.get("type") == "delivered":
            self.should_wake_up = True

    @workflow.signal
    async def inject_additional_instructions(self, new_rules: str) -> None:
        "Fires instantly when human operators submit mid-run parameter changes."
        self.runtime_instructions += f"\n[Human Override]: {new_rules}"
        self.should_wake_up = True

    @workflow.run
    async def run(self, order_id: str, initial_context: dict) -> dict:
        # Trigger an initial reasoning pass on genesis startup
        await workflow.execute_activity(
            execute_agent_reasoning_activity,
            {
                "order_id": order_id, 
                "trigger": "workflow_start", 
                "events": [initial_context], 
                "instructions": self.runtime_instructions
            },
            start_to_close_timeout=timedelta(seconds=60)
        )

        while not self.is_completed:
            # Efficiently sleep for up to 15 seconds, or wake early on high-priority signals
            woke_by_signal = await workflow.wait_condition(
                lambda: self.should_wake_up,
                timeout=timedelta(seconds=15)
            )

            # Take a thread-safe snapshot frame of events to prevent race conditions
            active_events = list(self.events_queue)
            self.events_queue.clear()
            self.should_wake_up = False

            # Check if any events mark delivery completion
            for event in active_events:
                if event.get("type") == "delivered":
                    self.is_completed = True

            trigger_type = "signal_event" if woke_by_signal else "scheduled_wakeup"

            # Execute a main agent reasoning pass
            await workflow.execute_activity(
                execute_agent_reasoning_activity,
                {
                    "order_id": order_id,
                    "trigger": trigger_type,
                    "events": active_events,
                    "instructions": self.runtime_instructions
                },
                start_to_close_timeout=timedelta(seconds=60)
            )

        # Generate structural final output when loops close down safely
        return await workflow.execute_activity(
            compile_final_summary_activity,
            order_id,
            start_to_close_timeout=timedelta(seconds=45)
        )
