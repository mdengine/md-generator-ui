from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QWidget,
)

from core.config_model import AppConfig, OcrStrategyUI


class ImageTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("Image OCR options")
        self._tess = QCheckBox("Tesseract (tess)")
        self._tess.setChecked(True)
        self._paddle = QCheckBox("PaddleOCR (paddle)")
        self._paddle.setChecked(True)
        self._easy = QCheckBox("EasyOCR (easy)")
        self._easy.setChecked(True)
        self._strategy = QComboBox()
        self._strategy.addItems(["best (multi-engine pick)", "fast (first selected engine only)"])
        self._tess_lang = QLineEdit("eng")
        self._paddle_lang = QLineEdit("en")
        self._easy_lang = QLineEdit("en")
        self._tess_cmd = QLineEdit()
        self._tess_cmd.setPlaceholderText("Optional path to tesseract executable")
        self._angle = QCheckBox("Paddle: use angle classifier")
        self._angle.setChecked(True)
        self._title = QLineEdit("OCR")
        form = QFormLayout()
        form.addRow(self._tess)
        form.addRow(self._paddle)
        form.addRow(self._easy)
        form.addRow("Strategy", self._strategy)
        form.addRow("Tesseract language", self._tess_lang)
        form.addRow("Paddle language", self._paddle_lang)
        form.addRow("EasyOCR languages (comma-separated)", self._easy_lang)
        form.addRow("Tesseract command", self._tess_cmd)
        form.addRow(self._angle)
        form.addRow("Document title", self._title)
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        i = cfg.image
        engines = set(i.engines)
        self._tess.setChecked("tess" in engines)
        self._paddle.setChecked("paddle" in engines)
        self._easy.setChecked("easy" in engines)
        self._strategy.setCurrentIndex(0 if i.strategy == OcrStrategyUI.BEST else 1)
        self._tess_lang.setText(i.tess_lang)
        self._paddle_lang.setText(i.paddle_lang)
        self._easy_lang.setText(i.easy_langs_csv)
        self._tess_cmd.setText(i.tesseract_cmd)
        self._angle.setChecked(i.paddle_use_angle_cls)
        self._title.setText(i.title)

    def apply_to(self, cfg: AppConfig) -> None:
        i = cfg.image
        eng: list[str] = []
        if self._tess.isChecked():
            eng.append("tess")
        if self._paddle.isChecked():
            eng.append("paddle")
        if self._easy.isChecked():
            eng.append("easy")
        i.engines = tuple(eng) if eng else ("tess",)
        i.strategy = OcrStrategyUI.BEST if self._strategy.currentIndex() == 0 else OcrStrategyUI.FAST
        i.tess_lang = self._tess_lang.text().strip() or "eng"
        i.paddle_lang = self._paddle_lang.text().strip() or "en"
        i.easy_langs_csv = self._easy_lang.text().strip() or "en"
        i.tesseract_cmd = self._tess_cmd.text().strip()
        i.paddle_use_angle_cls = self._angle.isChecked()
        i.title = self._title.text().strip() or "OCR"
