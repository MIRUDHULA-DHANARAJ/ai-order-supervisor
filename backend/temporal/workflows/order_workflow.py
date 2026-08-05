from datetime import timedelta

from temporalio import workflow

from backend.temporal.activities.order_activities import process_event


IMPORTANT_EVENTS = {
    "payment_failed",
    "shipment_delayed",
    "refund_requested",
    "customer_message_received",
    "delivered",
}


@workflow.defn
class OrderWorkflow:

    def __init__(self):
        self.events = []
        self.completed = False

        # Set to True when an important event arrives
        self.should_wake = False

    # Signals

    @workflow.signal
    async def receive_event(self, event: dict):
        """Receive an event from FastAPI."""

        self.events.append(event)

        if event.get("type") in IMPORTANT_EVENTS:
            self.should_wake = True

        if event.get("type") == "delivered":
            self.completed = True

    # Supervisor

    async def supervisor_cycle(self, trigger: str):
        """
        This is where the AI will reason.

        For now we only log why we woke up.
        """

        workflow.logger.info(f"Supervisor woke because of: {trigger}")

    # Activities
    

    async def process_events(self):
        "Process every pending event."

        while self.events:

            event = self.events.pop(0)

            result = await workflow.execute_activity(
                process_event,
                event,
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info(result)

    # Main Workflow
    

    @workflow.run
    async def run(self, order_id: str):

        workflow.logger.info(f"Workflow started for {order_id}")

        # Wake once when workflow starts
        await self.supervisor_cycle("workflow_start")

        while not self.completed:

            # Wait up to 10 seconds.
            # If an important event arrives before then,
            # the workflow wakes immediately.
            woke_by_event = await workflow.wait_condition(
                lambda: self.completed or self.should_wake,
                timeout=timedelta(seconds=10),
            )

            if self.completed:
                break

            if woke_by_event:
                trigger = "important_event"
                self.should_wake = False
            else:
                trigger = "scheduled_wakeup"

            # Process every queued event
            await self.process_events()

            # Run the supervisor
            await self.supervisor_cycle(trigger)

        workflow.logger.info(f"Workflow completed for {order_id}")