from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from enum import IntEnum

from .communication.client import ClientSender


class EventType(IntEnum):
    EventMessage = 0


@dataclass
class Event:
    type: EventType
    message: str


class Controller:
    def __init__(self, sender: ClientSender):
        self.sender: ClientSender = sender
        self.events: queue.SimpleQueue[Event | None] = queue.SimpleQueue()
        self._closed = threading.Event()
        self._listener_thread: threading.Thread | None = None
        self.init_listener()

    def get_events(self) -> queue.SimpleQueue[Event | None]:
        return self.events

    def send(self, content: str) -> None:
        self.sender.send(content)

    def init_listener(self) -> None:
        def listen():
            def on_message(buff: bytes) -> None:
                if not self._closed.is_set():
                    self.events.put(Event(EventType.EventMessage, buff.decode()))

            self.sender.listen(on_message)

        self._listener_thread = threading.Thread(target=listen, daemon=True)
        self._listener_thread.start()

    def close(self) -> None:
        self._closed.set()
        self.events.put(None)
        self.sender.close()
