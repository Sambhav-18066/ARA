from collections import defaultdict
from typing import Callable, Any


class EventBus:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event: str, callback: Callable):
        self.listeners[event].append(callback)

    def emit(self, event: str, data: Any = None):
        if event not in self.listeners:
            return

        for callback in self.listeners[event]:
            callback(data)


event_bus = EventBus()