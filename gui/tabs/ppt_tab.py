from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QWidget,
)

from core.config_model import AppConfig


class PptTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        box = QGroupBox("PowerPoint (.pptx) options")
        self._embed = QCheckBox("Extract embedded content (deep)")
        self._embed.setChecked(True)
        self._artifact = QComboBox()
        self._artifact.addItems(["Follow Common setting", "Force artifact layout", "Force classic (.md file)"])
        form = QFormLayout()
        form.addRow(self._embed)
        form.addRow("Artifact layout", self._artifact)
        form.addRow(QLabel("Classic mode writes a single .md next to extracted images."))
        box.setLayout(form)
        outer = QFormLayout()
        outer.addRow(box)
        self.setLayout(outer)

    def load_from(self, cfg: AppConfig) -> None:
        p = cfg.ppt
        self._embed.setChecked(p.extract_embedded_content)
        if p.artifact_layout_override is None:
            self._artifact.setCurrentIndex(0)
        elif p.artifact_layout_override:
            self._artifact.setCurrentIndex(1)
        else:
            self._artifact.setCurrentIndex(2)

    def apply_to(self, cfg: AppConfig) -> None:
        p = cfg.ppt
        p.extract_embedded_content = self._embed.isChecked()
        idx = self._artifact.currentIndex()
        p.artifact_layout_override = None if idx == 0 else (idx == 1)
