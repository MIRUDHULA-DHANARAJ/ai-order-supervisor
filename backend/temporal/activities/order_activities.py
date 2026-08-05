from temporalio import activity


@activity.defn
async def process_event(event: dict) -> str:
    activity.logger.info(f"Processing event: {event}")

    return f"Processed event: {event['type']}"