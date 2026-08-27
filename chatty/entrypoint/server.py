from __future__ import annotations

from ..communication.server import ConnectionManager
from ..communication.sockets import (
    SocketInfo,
    init_socket_default,
    set_socket_reusable,
    listen_for_client,
    close_socket,
)
from ..logger import init_logger
from ..utils import write_err


def launch_server() -> None:
    sock: SocketInfo | None = None
    try:
        init_logger("server")
        sock = init_socket_default()
        set_socket_reusable(sock)
        listen_for_client(sock, ConnectionManager())
    except Exception as err:
        write_err("Error while executing server", err)
    finally:
        if sock is not None:
            close_socket(sock)
