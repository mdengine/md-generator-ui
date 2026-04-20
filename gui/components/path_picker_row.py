"""Labeled path picker row."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class PathPickerRow(QWidget):
    pathChanged = Signal(str)

    def __init__(self, label: str, *, is_directory: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_directory = is_directory
        lay = QHBoxLayout(self)
        lay.addWidget(QLabel(label))
        self._edit = QLineEdit()
        self._edit.textChanged.connect(self.pathChanged.emit)
        lay.addWidget(self._edit, stretch=1)
        btn = QPushButton("Browse…")
        btn.clicked.connect(self._browse)
        lay.addWidget(btn)

    def path(self) -> str:
        return self._edit.text().strip()

    def set_path(self, p: str | Path) -> None:
        self._edit.setText(str(p))

    def _browse(self) -> None:
        start = self.path() or str(Path.home())
        if self._is_directory:
            d = QFileDialog.getExistingDirectory(self, "Select folder", start)
            if d:
                self._edit.setText(d)
        else:
            f, _ = QFileDialog.getOpenFileName(self, "Select file", start)
            if f:
                self._edit.setText(f)
