from __future__ import annotations

import socket
import threading
from dataclasses import dataclass, field

from .requests import Request, RequestType, serialize_request
from .sockets import (
    SocketInfo,
    accept_connections,
    listen_for_requests,
    read_request,
    send_all,
)
from ..utils import close_quietly


__all__ = [
    "ChatServer",
    "ConnectionManager",
]


@dataclass
class ConnectionManager:
    clients: dict[int, socket.socket] = field(default_factory=dict)
    usernames: dict[int, str] = field(default_factory=dict)
    mu: threading.RLock = field(default_factory=threading.RLock)

    def add_client(self, client: socket.socket, username: str) -> None:
        with self.mu:
            self.clients[client.fileno()] = client
            self.usernames[client.fileno()] = username

    def remove_client(self, client: socket.socket) -> None:
        with self.mu:
            fd = client.fileno()
            self.clients.pop(fd, None)
            self.usernames.pop(fd, None)

    def get_client_username(self, client: socket.socket) -> str:
        with self.mu:
            return self.usernames.get(client.fileno(), "anonymous")

    def list_clients(self) -> list[int]:
        with self.mu:
            return list(self.clients.keys())

    def write_to_clients(
        self,
        message: bytes | str,
        sender: socket.socket,
    ) -> None:
        sender_fd = sender.fileno() if hasattr(sender, "fileno") else sender
        for client_fd in self.list_clients():
            if client_fd != sender_fd:
                client = self.clients.get(client_fd)
                if client is not None:
                    send_all(client, message)


class ChatServer:
    def __init__(
        self,
        socket_info: SocketInfo,
        connection_manager: ConnectionManager,
    ) -> None:
        self.socket_info = socket_info
        self.connection_manager = connection_manager

    def serve_forever(self) -> None:
        accept_connections(self.socket_info, self._accept_client)

    def _accept_client(self, conn: socket.socket) -> None:
        auth_request = read_request(conn)
        if auth_request.type != RequestType.AuthAsk:
            conn.close()
            raise ValueError("expected auth request")

        username = auth_request.content.decode()
        self.connection_manager.add_client(conn, username)
        self._broadcast_presence(conn, f"{username} joined")

        thread = threading.Thread(
            target=self._listen_to_client,
            args=(conn,),
            daemon=True,
        )
        thread.start()

    def _listen_to_client(self, conn: socket.socket) -> None:
        try:
            listen_for_requests(
                conn,
                lambda request: self._handle_message(conn, request),
            )
        except EOFError:
            self._disconnect_client(conn)

    def _handle_message(
        self,
        conn: socket.socket,
        request: Request,
    ) -> None:
        if request.type != RequestType.MessageSend:
            return

        username = self.connection_manager.get_client_username(conn)
        message = f"{username}: {request.content.decode()}"
        print(f"--{message}--")
        self.connection_manager.write_to_clients(
            serialize_request(RequestType.MessageBroadCast, message),
            conn,
        )

    def _disconnect_client(self, conn: socket.socket) -> None:
        username = self.connection_manager.get_client_username(conn)
        self.connection_manager.remove_client(conn)
        self._broadcast_presence(conn, f"{username} left")
        close_quietly(conn)

    def _broadcast_presence(
        self,
        sender: socket.socket,
        message: str,
    ) -> None:
        self.connection_manager.write_to_clients(
            serialize_request(RequestType.MessageBroadCast, message),
            sender,
        )
