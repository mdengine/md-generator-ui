from __future__ import annotations

import copy

from PySide6.QtCore import QThread, Signal

from core.config_model import AppConfig
from services.url_service import preview_url_markdown


class UrlPreviewThread(QThread):
    preview_ok = Signal(str)
    preview_failed = Signal(str)

    def __init__(self, url: str, cfg: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self._url = url
        self._cfg = copy.deepcopy(cfg)

    def run(self) -> None:
        try:
            text = preview_url_markdown(self._url, self._cfg)
            self.preview_ok.emit(text)
        except Exception as e:
            self.preview_failed.emit(str(e))
