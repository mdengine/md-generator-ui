from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QWidget,
)

from core.config_model import AppConfig


class ZipTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("ZIP options")
        self._nested = QCheckBox("Enable nested ZIP expansion")
        self._nested.setChecked(True)
        self._depth = QSpinBox()
        self._depth.setRange(0, 64)
        self._depth.setValue(16)
        self._ocr_zip = QCheckBox("Enable OCR inside ZIP (raster post-pass)")
        self._use_img = QCheckBox("Run image-to-md post-pass on extracted rasters")
        self._use_img.setChecked(True)
        self._engines = QLineEdit("paddle,easy,tess")
        self._strategy = QLineEdit("best")
        form = QFormLayout()
        form.addRow(self._nested)
        form.addRow("Max nested ZIP depth", self._depth)
        form.addRow(self._ocr_zip)
        form.addRow(self._use_img)
        form.addRow("Image-to-md engines (comma-separated)", self._engines)
        form.addRow("Image-to-md strategy (best|compare)", self._strategy)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        z = cfg.zip
        self._nested.setChecked(z.nested_conversions)
        self._depth.setValue(z.max_nested_depth)
        self._ocr_zip.setChecked(z.ocr_inside_zip)
        self._use_img.setChecked(z.use_image_to_md)
        self._engines.setText(z.image_to_md_engines)
        self._strategy.setText(z.image_to_md_strategy)

    def apply_to(self, cfg: AppConfig) -> None:
        z = cfg.zip
        z.nested_conversions = self._nested.isChecked()
        z.max_nested_depth = int(self._depth.value())
        z.ocr_inside_zip = self._ocr_zip.isChecked()
        z.use_image_to_md = self._use_img.isChecked()
        z.image_to_md_engines = self._engines.text().strip() or "paddle,easy,tess"
        z.image_to_md_strategy = self._strategy.text().strip() or "best"
