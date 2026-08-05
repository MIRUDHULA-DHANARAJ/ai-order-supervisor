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
        self.is_paused: bool = False  # Track pause state natively

    @workflow.signal
    async def process_signal_event(self, event: dict) -> None:
        self.events_queue.append(event)
        is_critical = await workflow.execute_activity(
            classify_incoming_event_activity,
            event,
            start_to_close_timeout=timedelta(seconds=10)
        )
        if (is_critical or event.get("type") == "delivered") and not self.is_paused:
            self.should_wake_up = True

    @workflow.signal
    async def inject_additional_instructions(self, new_rules: str) -> None:
        self.runtime_instructions += f"\n[Human Override]: {new_rules}"
        if not self.is_paused:
            self.should_wake_up = True

    @workflow.signal
    async def pause_workflow(self) -> None:
        """Natively blocks supervisor inference passes."""
        self.is_paused = True
        self.should_wake_up = True

    @workflow.signal
    async def resume_workflow(self) -> None:
        """Natively unblocks supervisor inference passes."""
        self.is_paused = False
        self.should_wake_up = True

    @workflow.run
    async def run(self, order_id: str, initial_context: dict) -> dict:
        await workflow.execute_activity(
            execute_agent_reasoning_activity,
            {"order_id": order_id, "trigger": "workflow_start", "events": [initial_context], "instructions": self.runtime_instructions},
            start_to_close_timeout=timedelta(seconds=60)
        )

        while not self.is_completed:
            woke_by_signal = await workflow.wait_condition(
                lambda: self.should_wake_up,
                timeout=timedelta(seconds=15)
            )

            # If paused by human node, do not process actions or clear event queues
            if self.is_paused:
                self.should_wake_up = False
                continue

            active_events = list(self.events_queue)
            self.events_queue.clear()
            self.should_wake_up = False

            for event in active_events:
                if event.get("type") == "delivered":
                    self.is_completed = True

            trigger_type = "signal_event" if woke_by_signal else "scheduled_wakeup"

            await workflow.execute_activity(
                execute_agent_reasoning_activity,
                {"order_id": order_id, "trigger": trigger_type, "events": active_events, "instructions": self.runtime_instructions},
                start_to_close_timeout=timedelta(seconds=60)
            )

        return await workflow.execute_activity(
            compile_final_summary_activity,
            {"order_id": order_id, "instructions": self.runtime_instructions},
            start_to_close_timeout=timedelta(seconds=45)
        )
