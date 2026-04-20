"""Shared conversion options (output, layout, logging)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from core.config_model import AppConfig


class CommonPanel(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Common", parent)
        self._out = QLineEdit()
        self._out.setPlaceholderText("Output directory")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_out)
        row = QHBoxLayout()
        row.addWidget(self._out, 1)
        row.addWidget(browse)

        self._artifact = QCheckBox("Artifact layout (document.md + assets/)")
        self._verbose = QCheckBox("Verbose logging")
        self._overwrite = QCheckBox("Overwrite existing outputs")

        form = QFormLayout()
        form.addRow("Output directory", row)
        form.addRow(self._artifact)
        form.addRow(self._verbose)
        form.addRow(self._overwrite)
        self.setLayout(form)

    def _browse_out(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Output directory", self._out.text() or str(Path.home()))
        if d:
            self._out.setText(d)

    def load_from(self, cfg: AppConfig) -> None:
        c = cfg.common
        self._out.setText(str(c.output_dir))
        self._artifact.setChecked(c.artifact_layout)
        self._verbose.setChecked(c.verbose)
        self._overwrite.setChecked(c.overwrite)

    def apply_to(self, cfg: AppConfig) -> None:
        c = cfg.common
        c.output_dir = Path(self._out.text().strip() or str(Path.home() / "md-generator-out"))
        c.artifact_layout = self._artifact.isChecked()
        c.verbose = self._verbose.isChecked()
        c.overwrite = self._overwrite.isChecked()
