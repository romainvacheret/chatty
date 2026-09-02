from __future__ import annotations

import curses
import threading

from .core import Controller, Event, EventType


__all__ = ["ClientTui"]


VIEW_DISPLAY = "display"
VIEW_INPUT = "input"


class ClientTui:
    def __init__(self, controller: Controller):
        self.controller: Controller = controller
        self.gui: curses.window | None = None
        self._messages: list[str] = []
        self._lock = threading.RLock()
        self._closed = threading.Event()
        self._event_thread = threading.Thread(
            target=self.init_event_listener, daemon=True
        )
        self._event_thread.start()

    def init_event_listener(self) -> None:
        events = self.controller.get_events()
        while not self._closed.is_set():
            event = events.get()
            if event is None:
                break
            if event.type == EventType.EventMessage:
                self.handle_message(event)

    def handle_message(self, event: Event) -> None:
        with self._lock:
            self._messages.append(event.message.strip())

    def run_main_loop(self) -> None:
        try:
            curses.wrapper(self._main_loop)
        except KeyboardInterrupt:
            self.close()

    def _main_loop(self, stdscr: curses.window) -> None:
        self.gui = stdscr
        stdscr.keypad(True)
        curses.curs_set(1)
        stdscr.timeout(100)

        input_buffer: list[str] = []

        while not self._closed.is_set():
            self._render(stdscr, input_buffer)
            ch = stdscr.getch()

            if ch == -1:
                continue

            if ch in (3,):
                self.close()
                break

            if ch in (curses.KEY_ENTER, 10, 13):
                self.submit_message("".join(input_buffer))
                input_buffer = []
                continue

            if ch in (curses.KEY_BACKSPACE, 127, 8):
                if input_buffer:
                    input_buffer.pop()
                continue

            if 0 <= ch < 256:
                char = chr(ch)
                if char.isprintable():
                    input_buffer.append(char)

    def _render(self, stdscr: curses.window, input_buffer: list[str]) -> None:
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        try:
            stdscr.addstr(0, 0, "Messages"[: max(0, width - 1)])
        except curses.error:
            pass

        with self._lock:
            visible_lines = self._messages[:]

        message_limit = max(0, height - 4)
        if message_limit and len(visible_lines) > message_limit:
            visible_lines = visible_lines[-message_limit:]

        for row, line in enumerate(visible_lines, start=1):
            if row >= height - 3:
                break
            try:
                stdscr.addstr(row, 0, line[: max(0, width - 1)])
            except curses.error:
                pass

        input_title_row = max(0, height - 3)
        input_row = max(0, height - 2)

        try:
            stdscr.addstr(input_title_row, 0, "Input"[: max(0, width - 1)])
            stdscr.addstr(input_row, 0, "".join(input_buffer)[: max(0, width - 1)])
            stdscr.move(input_row, min(len(input_buffer), max(0, width - 1)))
        except curses.error:
            pass

        stdscr.refresh()

    def submit_message(self, input_value: str) -> None:
        input_value = input_value.strip()

        if input_value != "":
            self.controller.send(input_value)
            with self._lock:
                self._messages.append(input_value)

    def close(self) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        self.controller.close()
