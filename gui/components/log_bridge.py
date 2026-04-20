"""Thread-safe logging bridge into Qt."""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal


class LogBridge(QObject):
    message = Signal(str)


class GuiLogHandler(logging.Handler):
    def __init__(self, bridge: LogBridge) -> None:
        super().__init__()
        self._bridge = bridge

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._bridge.message.emit(msg)
        except Exception:  # noqa: BLE001
            self.handleError(record)
