from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .. import logger


DELIMITER = "\n"
FIELD_SEP = "|"


class RequestType(IntEnum):
    AuthAsk = 0
    MessageSend = 1
    MessageBroadCast = 2


@dataclass
class Request:
    type: RequestType
    content: bytes


def serialize_request(kind: RequestType, content: bytes | str) -> bytes:
    if isinstance(content, str):
        content = content.encode()
    header = f"{int(kind)}{FIELD_SEP}{len(content)}{DELIMITER}".encode()
    return header + content


def parse_request(buff: bytes) -> Request:
    header, sep, payload = buff.partition(DELIMITER.encode())

    if not sep:
        if logger.Logger is not None:
            logger.Logger.error(
                "Error - unexpected request buffer format: %s",
                buff.decode(errors="replace"),
            )
        raise ValueError("unexpected request buffer format")

    try:
        kind_raw, length_raw = header.decode().split(FIELD_SEP, 1)
        kind = RequestType(int(kind_raw))
        expected_len = int(length_raw)
    except (ValueError, KeyError):
        if logger.Logger is not None:
            logger.Logger.error(
                "Error - invalid request header: %s",
                header.decode(errors="replace"),
            )
        raise ValueError("invalid request header")

    if len(payload) != expected_len:
        if logger.Logger is not None:
            logger.Logger.error(
                "Error - request length mismatch: expected %s got %s",
                expected_len,
                len(payload),
            )
        raise ValueError("request length mismatch")

    return Request(type=kind, content=payload)
