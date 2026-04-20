"""Queue-based logging bridged to the Qt GUI thread."""

from __future__ import annotations

import logging
import queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QObject, SignalInstance


class QtLogEmitter:
    """Install on a QObject that defines ``signal = Signal(str)`` for log lines."""

    def __init__(self, signal: SignalInstance) -> None:
        self._signal = signal
        self._q: queue.Queue[str] = queue.Queue(-1)

    def emit_line(self, line: str) -> None:
        self._q.put(line.rstrip("\n"))

    def flush_pending(self) -> None:
        while True:
            try:
                line = self._q.get_nowait()
            except queue.Empty:
                break
            self._signal.emit(line)


def setup_root_logger(
    *,
    verbose: bool,
    qt_emitter: QtLogEmitter | None,
) -> logging.Handler:
    """Configure root logger; return the queue handler for optional removal."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)

    class _QtHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            if qt_emitter is None:
                return
            try:
                msg = self.format(record)
                qt_emitter.emit_line(msg)
            except Exception:
                self.handleError(record)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    qh = _QtHandler()
    qh.setFormatter(fmt)
    root.addHandler(qh)

    if verbose:
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        root.addHandler(ch)

    return qh
