from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from .requests import RequestType, serialize_request
from .sockets import write


@dataclass
class ConnectionManager:
    clients: dict[int, Any] = field(default_factory=dict)
    usernames: dict[int, str] = field(default_factory=dict)
    mu: threading.RLock = field(default_factory=threading.RLock)

    def add_client(self, client: Any, username: str) -> None:
        with self.mu:
            self.clients[client.fileno()] = client
            self.usernames[client.fileno()] = username

    def remove_client(self, client: Any) -> None:
        with self.mu:
            fd = client.fileno()
            self.clients.pop(fd, None)
            self.usernames.pop(fd, None)

    def get_client_username(self, client: Any) -> str:
        with self.mu:
            return self.usernames.get(client.fileno(), "anonymous")

    def list_clients(self) -> list[int]:
        with self.mu:
            return list(self.clients.keys())

    def write_to_clients(self, message: bytes | str, sender: Any) -> None:
        sender_fd = sender.fileno() if hasattr(sender, "fileno") else sender
        for client_fd in self.list_clients():
            if client_fd != sender_fd:
                client = self.clients.get(client_fd)
                if client is not None:
                    write(client, message)

    def broadcast_join(self, client: Any) -> None:
        username = self.get_client_username(client)
        self.write_to_clients(
            serialize_request(RequestType.MessageBroadCast, f"{username} joined"),
            client,
        )

    def broadcast_leave(self, client: Any) -> None:
        username = self.get_client_username(client)
        self.write_to_clients(
            serialize_request(RequestType.MessageBroadCast, f"{username} left"),
            client,
        )
