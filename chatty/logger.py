from __future__ import annotations

import logging
from logging import Logger as LoggingLogger

from .utils import write_err


Logger: LoggingLogger | None = None


def init_logger(name: str) -> None:
    global Logger

    file_handler = logging.FileHandler(f"{name}.log", mode="a", encoding="utf-8")
    logger = logging.getLogger(f"chatty.{name}")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    file_handler.setFormatter(
        logging.Formatter("DEBUG: %(asctime)s %(filename)s:%(lineno)d %(message)s")
    )
    logger.addHandler(file_handler)
    Logger = logger
