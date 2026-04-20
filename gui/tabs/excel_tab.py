from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QWidget

from core.config_model import AppConfig


class ExcelTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("Excel / CSV options")
        self._split = QCheckBox("Split sheets (one Markdown file per sheet when applicable)")
        form = QFormLayout()
        form.addRow(self._split)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        self._split.setChecked(cfg.excel.split_sheets)

    def apply_to(self, cfg: AppConfig) -> None:
        cfg.excel.split_sheets = self._split.isChecked()
