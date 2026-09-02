import unittest

from chatty.communication.requests import RequestType, serialize_request
from chatty.communication.sockets import read_request, send_all


class PartialSocket:
    def __init__(self):
        self.calls = []

    def send(self, data):
        size = min(2, len(data))
        self.calls.append(data[:size])
        return size


class ReceivingSocket:
    def __init__(self, data):
        self.data = bytearray(data)

    def recv(self, size):
        if not self.data:
            return b""

        size = min(size, 2)
        result = bytes(self.data[:size])
        del self.data[:size]
        return result


class SocketTests(unittest.TestCase):
    def test_read_request_from_socket(self):
        sock = ReceivingSocket(
            serialize_request(RequestType.MessageSend, "hello")
        )

        request = read_request(sock)

        self.assertEqual(request.type, RequestType.MessageSend)
        self.assertEqual(request.content, b"hello")

    def test_read_request_detects_closed_socket(self):
        with self.assertRaises(EOFError):
            read_request(ReceivingSocket(b""))

    def test_send_all_handles_partial_sends(self):
        sock = PartialSocket()
        payload = b"abcdef"

        send_all(sock, payload)

        self.assertEqual(b"".join(sock.calls), payload)


if __name__ == "__main__":
    unittest.main()
