from __future__ import annotations

from typing import Callable

from .sockets import BUFF_SIZE, close_socket, listen_for_message, write
from .sockets import SocketInfo
from ..utils import pad_bytes


class ClientSender:
    def __init__(self, sock: SocketInfo):
        self.server_socket: SocketInfo = sock

    def send(self, message: str) -> None:
        write(self.server_socket.sock, pad_bytes(message, BUFF_SIZE))

    def listen(self, callback: Callable[[bytes], None]) -> None:
        listen_for_message(self.server_socket.sock, callback)

    def close(self) -> None:
        close_socket(self.server_socket)
