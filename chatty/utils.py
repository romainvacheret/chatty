from __future__ import annotations

from contextlib import suppress
from sys import stderr
from typing import Protocol


class Closeable(Protocol):
    def close(self) -> None:
        ...


def write_err(msg: str, err: object) -> None:
    print(f"{msg}: {err}", file=stderr)


def remove_padding(buff: bytes | str) -> str:
    if isinstance(buff, bytes):
        buff = buff.decode()
    return buff.rstrip()


def pad_bytes(buff: bytes | str, size: int) -> bytes:
    if isinstance(buff, str):
        buff = buff.encode()
    if len(buff) >= size:
        return buff
    return buff + (b" " * (size - len(buff)))


def close_quietly(resource: Closeable) -> None:
    with suppress(OSError):
        resource.close()
