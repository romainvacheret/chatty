from __future__ import annotations

from typing import Callable

from .requests import Request, RequestType, serialize_request
from .sockets import close_socket, listen_for_requests, send_all
from .sockets import SocketInfo


__all__ = ["ClientSender"]


class ClientSender:
    def __init__(self, sock: SocketInfo):
        self.socket: SocketInfo = sock

    def send_auth(self, username: str) -> None:
        send_all(
            self.socket.sock,
            serialize_request(RequestType.AuthAsk, username),
        )

    def send(self, message: str) -> None:
        send_all(
            self.socket.sock,
            serialize_request(RequestType.MessageSend, message),
        )

    def listen(self, callback: Callable[[Request], None]) -> None:
        listen_for_requests(self.socket.sock, callback)

    def close(self) -> None:
        close_socket(self.socket)
