import socket
import unittest
from unittest.mock import Mock, patch

from chatty.communication.server import ConnectionManager


class ConnectionManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = ConnectionManager()
        self.client_a = Mock(spec=socket.socket)
        self.client_b = Mock(spec=socket.socket)
        self.client_a.fileno.return_value = 1
        self.client_b.fileno.return_value = 2

    def test_add_and_remove_client(self):
        self.manager.add_client(self.client_a, "alice")

        self.assertEqual(
            self.manager.get_client_username(self.client_a),
            "alice",
        )
        self.assertIn(self.client_a.fileno(), self.manager.list_clients())

        self.manager.remove_client(self.client_a)

        self.assertEqual(
            self.manager.get_client_username(self.client_a),
            "anonymous",
        )

    @patch("chatty.communication.server.send_all")
    def test_write_to_clients_excludes_sender(self, send_all):
        self.manager.add_client(self.client_a, "alice")
        self.manager.add_client(self.client_b, "bob")

        self.manager.write_to_clients(b"message", self.client_a)

        send_all.assert_called_once_with(self.client_b, b"message")


if __name__ == "__main__":
    unittest.main()
