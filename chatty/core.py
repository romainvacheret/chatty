from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from enum import IntEnum

from .communication.client import ClientSender
from .communication.requests import Request, RequestType


__all__ = [
    "Controller",
    "Event",
    "EventType",
]


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

    def get_events(self) -> queue.SimpleQueue[Event | None]:
        return self.events

    def send(self, content: str) -> None:
        self.sender.send(content)

    def start(self) -> None:
        if self._listener_thread is not None:
            return

        self._listener_thread = threading.Thread(
            target=self._listen,
            daemon=True,
        )
        self._listener_thread.start()

    def _listen(self) -> None:
        def on_message(request: Request) -> None:
            self._handle_request(request)

        self.sender.listen(on_message)

    def _handle_request(self, request: Request) -> None:
        if self._closed.is_set():
            return

        if request.type == RequestType.MessageBroadCast:
            self.events.put(
                Event(
                    EventType.EventMessage,
                    request.content.decode(),
                )
            )

    def close(self) -> None:
        if self._closed.is_set():
            return

        self._closed.set()
        self.events.put(None)
        self.sender.close()
