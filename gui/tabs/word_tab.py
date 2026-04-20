from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QWidget,
)

from core.config_model import AppConfig


class WordTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("Word (.docx) options")
        self._img_dir = QLineEdit("images")
        self._page_break = QCheckBox("Render page breaks as horizontal rules")
        self._page_break.setChecked(True)
        form = QFormLayout()
        form.addRow("Extract images directory (classic layout)", self._img_dir)
        form.addRow(self._page_break)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        w = cfg.word
        self._img_dir.setText(w.extract_images_dir)
        self._page_break.setChecked(w.page_break_as_hr)

    def apply_to(self, cfg: AppConfig) -> None:
        w = cfg.word
        w.extract_images_dir = self._img_dir.text().strip() or "images"
        w.page_break_as_hr = self._page_break.isChecked()
