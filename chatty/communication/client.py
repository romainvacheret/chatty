from __future__ import annotations

from typing import Callable

from .requests import Request, RequestType, serialize_request
from .sockets import close_socket, listen_for_message, write
from .sockets import SocketInfo


class ClientSender:
    def __init__(self, sock: SocketInfo):
        self.server_socket: SocketInfo = sock

    def send_auth(self, username: str) -> None:
        write(
            self.server_socket.sock,
            serialize_request(RequestType.AuthAsk, username),
        )

    def send(self, message: str) -> None:
        write(
            self.server_socket.sock,
            serialize_request(RequestType.MessageSend, message),
        )

    def listen(self, callback: Callable[[Request], None]) -> None:
        listen_for_message(self.server_socket.sock, callback)

    def close(self) -> None:
        close_socket(self.server_socket)
