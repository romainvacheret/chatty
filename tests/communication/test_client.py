import socket
import unittest
from unittest.mock import Mock, patch

from chatty.communication.client import ClientSender
from chatty.communication.requests import RequestType, serialize_request
from chatty.communication.sockets import SocketInfo


class ClientSenderTests(unittest.TestCase):
    def setUp(self):
        self.sock = Mock(spec=socket.socket)
        self.sender = ClientSender(
            SocketInfo(self.sock, ("127.0.0.1", 1234))
        )

    @patch("chatty.communication.client.send_all")
    def test_send_auth_serializes_username(self, send_all):
        self.sender.send_auth("alice")

        send_all.assert_called_once_with(
            self.sock,
            serialize_request(RequestType.AuthAsk, "alice"),
        )

    @patch("chatty.communication.client.send_all")
    def test_send_serializes_message(self, send_all):
        self.sender.send("hello")

        send_all.assert_called_once_with(
            self.sock,
            serialize_request(RequestType.MessageSend, "hello"),
        )


if __name__ == "__main__":
    unittest.main()
