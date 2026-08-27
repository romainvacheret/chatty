from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from typing import Any, Callable

from .requests import Request, RequestType, parse_request, serialize_request
from ..utils import close_quietly


BUFF_SIZE = 2048
SOCK_PORT = 1234
SOCK_ADDR = ("127.0.0.1", 1234)


@dataclass
class SocketInfo:
    sock: socket.socket
    addr: tuple[str, int]

    @property
    def fd(self) -> int:
        return self.sock.fileno()


def init_socket(port: int = SOCK_PORT, addr: tuple[str, int] = ("127.0.0.1", 0)) -> SocketInfo:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return SocketInfo(sock=sock, addr=(addr[0], port))


def init_socket_default() -> SocketInfo:
    return init_socket(SOCK_PORT, SOCK_ADDR)


def set_socket_reusable(sock_info: SocketInfo) -> None:
    sock_info.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def _read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise EOFError("socket closed")
        chunks.extend(chunk)
    return bytes(chunks)


def write(sock: socket.socket, buff: bytes | str) -> None:
    if isinstance(buff, str):
        buff = buff.encode()

    total_written = 0
    while total_written < len(buff):
        nb = sock.send(buff[total_written:])
        if nb == 0:
            raise EOFError("socket closed")
        total_written += nb


def connect_socket(sock_info: SocketInfo) -> None:
    sock_info.sock.connect(sock_info.addr)


def close_socket(sock_info: SocketInfo) -> None:
    close_quietly(sock_info.sock)


def _read_request(conn: socket.socket) -> Request:
    header = bytearray()
    while True:
        chunk = conn.recv(1)
        if not chunk:
            raise EOFError("socket closed")
        header.extend(chunk)
        if header.endswith(b"\n"):
            break

    kind_raw, length_raw = header[:-1].decode().split("|", 1)
    payload = _read_exact(conn, int(length_raw))
    return parse_request(bytes(header) + payload)


def listen_for_message(conn: socket.socket, callback: Callable[[Request], None]) -> None:
    while True:
        callback(_read_request(conn))


def listen_for_client(
    sock_info: SocketInfo, connection_manager: Any
) -> None:
    sock_info.sock.bind(sock_info.addr)
    sock_info.sock.listen(socket.SOMAXCONN)

    while True:
        conn, _ = sock_info.sock.accept()
        auth_request = _read_request(conn)
        if auth_request.type != RequestType.AuthAsk:
            raise ValueError("expected auth request")
        username = auth_request.content.decode()
        connection_manager.add_client(conn, username)
        connection_manager.broadcast_join(conn)

        def on_message(msg: Request, conn: socket.socket = conn) -> None:
            if msg.type != RequestType.MessageSend:
                return
            username = connection_manager.get_client_username(conn)
            message = f"{username}: {msg.content.decode()}"
            print(f"--{message}--")
            connection_manager.write_to_clients(
                serialize_request(RequestType.MessageBroadCast, message),
                conn,
            )

        def on_disconnect(conn: socket.socket = conn) -> None:
            connection_manager.remove_client(conn)
            connection_manager.broadcast_leave(conn)
            close_quietly(conn)

        def listen_client() -> None:
            try:
                listen_for_message(conn, on_message)
            except EOFError:
                on_disconnect()

        thread = threading.Thread(target=listen_client, daemon=True)
        thread.start()
