import unittest

from chatty.communication.requests import (
    RequestType,
    parse_request,
    serialize_request,
)


class RequestTests(unittest.TestCase):
    def test_serialize_and_parse_text_request(self):
        encoded = serialize_request(RequestType.MessageSend, "hello")
        request = parse_request(encoded)

        self.assertEqual(request.type, RequestType.MessageSend)
        self.assertEqual(request.content, b"hello")

    def test_length_is_measured_in_bytes(self):
        encoded = serialize_request(RequestType.MessageSend, "é")

        self.assertTrue(encoded.startswith(b"1|2\n"))

    def test_parse_rejects_invalid_length(self):
        with self.assertRaises(ValueError):
            parse_request(b"1|10\nhello")

    def test_parse_rejects_invalid_header(self):
        with self.assertRaises(ValueError):
            parse_request(b"invalid\nhello")


if __name__ == "__main__":
    unittest.main()
