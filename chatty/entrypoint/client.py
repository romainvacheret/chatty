from __future__ import annotations

from ..communication.client import ClientSender
from ..communication.sockets import SocketInfo, init_socket_default, connect_socket
from ..core import Controller
from ..logger import init_logger
from ..tui import ClientTui
from ..utils import write_err


def launch_client() -> None:
    try:
        init_logger("client")
        sock: SocketInfo = init_socket_default()
        connect_socket(sock)

        username = input("Username: ").strip() or "anonymous"
        sender = ClientSender(sock)
        sender.send(username)
        controller = Controller(sender)
        tui = ClientTui(controller)
        tui.run_main_loop()
    except Exception as err:
        write_err("Error while executing client", err)
