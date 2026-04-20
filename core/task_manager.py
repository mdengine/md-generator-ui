"""Background conversion thread with cooperative cancel."""

from __future__ import annotations

import logging
import threading
import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from core.config_model import AppConfig, InputMode
from services.batch_processor import BatchItem, build_items_from_paths, build_items_from_urls, process_item

logger = logging.getLogger(__name__)


class ConversionThread(QThread):
    log_line = Signal(str)
    progress = Signal(int, int)  # value, maximum
    finished = Signal(bool, str)  # success, message

    def __init__(self, cfg: AppConfig, paths: list[Path], urls: list[str], parent=None) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._paths = paths
        self._urls = urls
        self._cancel = threading.Event()

    def request_cancel(self) -> None:
        self._cancel.set()

    def _emit(self, msg: str) -> None:
        self.log_line.emit(msg)

    def run(self) -> None:  # noqa: PLR0911
        cfg = self._cfg
        try:
            if cfg.url.crawl and not cfg.effective_artifact(for_url=True):
                self.finished.emit(False, "URL crawl requires artifact layout. Enable it in Common or URL tab.")
                return

            items: list[BatchItem] = []
            if cfg.input_mode == InputMode.URL:
                items = build_items_from_urls(self._urls)
            else:
                items = build_items_from_paths(self._paths, input_mode=cfg.input_mode)

            if not items:
                self.finished.emit(False, "Nothing to convert (empty queue or unsupported files).")
                return

            total = len(items)
            self._emit(f"Starting batch: {total} item(s).")
            self.progress.emit(0, total)

            for i, item in enumerate(items, start=1):
                if self._cancel.is_set():
                    self._emit("Cancelled by user.")
                    self.finished.emit(False, "Cancelled")
                    return
                label = item.url or item.urls or (str(item.path) if item.path else "?")
                self._emit(f"[{i}/{total}] {label}")
                try:
                    out = process_item(item, cfg, cancel=self._cancel, on_tick=None)
                    self._emit(f"  → wrote: {out}")
                except Exception as e:
                    logger.exception("Item failed")
                    self._emit(f"  ERROR: {e}")
                    self._emit(traceback.format_exc())
                self.progress.emit(i, total)

            self.finished.emit(True, "Done.")
        except Exception as e:
            logger.exception("Batch failed")
            self.finished.emit(False, str(e))
