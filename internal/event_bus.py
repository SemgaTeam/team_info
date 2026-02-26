class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, events):
        for event in events:
            for handler in self._handlers.get(type(event), []):
                await handler(event)