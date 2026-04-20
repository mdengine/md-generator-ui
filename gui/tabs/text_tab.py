from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QWidget,
)

from core.config_model import AppConfig


class TextTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("Text / JSON / XML options")
        self._encoding = QLineEdit("utf-8")
        self._fmt = QComboBox()
        self._fmt.addItems(["auto", "txt", "json", "xml"])
        self._src = QCheckBox("Include fenced source block (JSON/XML)")
        self._src.setChecked(True)
        self._toc = QCheckBox("Generate table of contents (JSON/XML)")
        form = QFormLayout()
        form.addRow("Encoding", self._encoding)
        form.addRow("Input format", self._fmt)
        form.addRow(self._src)
        form.addRow(self._toc)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        t = cfg.text
        self._encoding.setText(t.encoding)
        vals = ["auto", "txt", "json", "xml"]
        try:
            idx = vals.index(t.input_format)
        except ValueError:
            idx = 0
        self._fmt.setCurrentIndex(idx)
        self._src.setChecked(t.include_source_block)
        self._toc.setChecked(t.generate_toc)

    def apply_to(self, cfg: AppConfig) -> None:
        t = cfg.text
        t.encoding = self._encoding.text().strip() or "utf-8"
        t.input_format = self._fmt.currentText()  # type: ignore[assignment]
        t.include_source_block = self._src.isChecked()
        t.generate_toc = self._toc.isChecked()
