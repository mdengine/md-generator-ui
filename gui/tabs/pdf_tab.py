from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QWidget,
)

from core.config_model import AppConfig


class PdfTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("PDF options")
        self._extract_img = QCheckBox("Extract images (embed in Markdown)")
        self._extract_img.setChecked(True)
        self._ocr = QCheckBox("Fallback OCR when page has few characters")
        self._ocr_min = QSpinBox()
        self._ocr_min.setRange(1, 5000)
        self._ocr_min.setValue(40)
        form = QFormLayout()
        form.addRow(self._extract_img)
        form.addRow(self._ocr)
        form.addRow("OCR min characters", self._ocr_min)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        p = cfg.pdf
        self._extract_img.setChecked(p.extract_images)
        self._ocr.setChecked(p.use_ocr)
        self._ocr_min.setValue(p.ocr_min_chars)

    def apply_to(self, cfg: AppConfig) -> None:
        p = cfg.pdf
        p.extract_images = self._extract_img.isChecked()
        p.use_ocr = self._ocr.isChecked()
        p.ocr_min_chars = int(self._ocr_min.value())
