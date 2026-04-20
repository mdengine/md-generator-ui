"""Entry point for md-generator-ui (PySide6)."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def _load_stylesheet(base: Path) -> str | None:
    qss = base / "assets" / "app.qss"
    if qss.is_file():
        return qss.read_text(encoding="utf-8")
    return None


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("md-generator-ui")
    app.setOrganizationName("md-generator-ui")

    root = Path(__file__).resolve().parent
    icon = root / "assets" / "app.png"
    if icon.is_file():
        app.setWindowIcon(QIcon(str(icon)))

    style = _load_stylesheet(root)
    if style:
        app.setStyleSheet(style)

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
