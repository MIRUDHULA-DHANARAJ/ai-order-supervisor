import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from temporal.workflows.order_workflow import OrderWorkflow
from temporal.activities.order_activities import health_check
from temporal.activities.order_activities import process_event



async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="order-supervisor",
        workflows=[OrderWorkflow],
        activities=[process_event],
    )

    print("Worker started...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())