from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.config_model import AppConfig


class UrlTab(QWidget):
    """URL crawl/fetch options, multi-line URLs, and preview trigger."""

    preview_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._urls = QPlainTextEdit()
        self._urls.setPlaceholderText("One URL per line…")
        self._crawl = QCheckBox("Crawl linked pages (requires artifact layout)")
        self._async_crawl = QCheckBox("Use async crawl (when crawling)")
        self._depth = QSpinBox()
        self._depth.setRange(0, 20)
        self._depth.setValue(2)
        self._max_pages = QSpinBox()
        self._max_pages.setRange(1, 10_000)
        self._max_pages.setValue(30)
        self._download = QCheckBox("Download linked files")
        self._download.setChecked(True)
        self._robots = QCheckBox("Obey robots.txt")
        self._robots.setChecked(True)
        self._same_site = QCheckBox("Same site only")
        self._same_site.setChecked(True)
        self._subdomains = QCheckBox("Include subdomains")
        self._subdomains.setChecked(True)
        self._delay = QDoubleSpinBox()
        self._delay.setRange(0.0, 60.0)
        self._delay.setSingleStep(0.1)
        self._delay.setValue(0.5)
        self._timeout = QDoubleSpinBox()
        self._timeout.setRange(1.0, 600.0)
        self._timeout.setValue(30.0)
        self._max_mb = QSpinBox()
        self._max_mb.setRange(1, 512)
        self._max_mb.setValue(10)
        self._artifact = QComboBox()
        self._artifact.addItems(["Follow Common setting", "Force artifact layout", "Force classic (.md file)"])

        self._preview = QPushButton("Preview first URL (fetch → Markdown)")
        self._preview.clicked.connect(self.preview_requested.emit)

        opts = QGroupBox("URL options")
        form = QFormLayout()
        form.addRow("Seed URLs", self._urls)
        form.addRow(self._crawl)
        form.addRow(self._async_crawl)
        form.addRow("Crawl max depth", self._depth)
        form.addRow("Max pages", self._max_pages)
        form.addRow("Crawl delay (seconds)", self._delay)
        form.addRow(self._download)
        form.addRow(self._robots)
        form.addRow(self._same_site)
        form.addRow(self._subdomains)
        form.addRow("HTTP timeout (seconds)", self._timeout)
        form.addRow("Max response size (MiB)", self._max_mb)
        form.addRow("Artifact layout", self._artifact)
        form.addRow(QLabel("Bulk URL conversion always writes an index under the output folder."))
        opts.setLayout(form)

        lay = QVBoxLayout()
        lay.addWidget(opts)
        lay.addWidget(self._preview)
        self.setLayout(lay)

    def urls_text(self) -> str:
        return self._urls.toPlainText()

    def set_urls_text(self, text: str) -> None:
        self._urls.setPlainText(text)

    def load_from(self, cfg: AppConfig) -> None:
        u = cfg.url
        self._crawl.setChecked(u.crawl)
        self._async_crawl.setChecked(u.async_crawl)
        self._depth.setValue(u.crawl_depth)
        self._max_pages.setValue(u.max_pages)
        self._download.setChecked(u.download_linked_files)
        self._robots.setChecked(u.obey_robots)
        self._same_site.setChecked(u.same_site_only)
        self._subdomains.setChecked(u.include_subdomains)
        self._delay.setValue(u.crawl_delay_seconds)
        self._timeout.setValue(u.timeout_seconds)
        self._max_mb.setValue(max(1, u.max_response_bytes // (1024 * 1024)))
        if u.artifact_layout_override is None:
            self._artifact.setCurrentIndex(0)
        elif u.artifact_layout_override:
            self._artifact.setCurrentIndex(1)
        else:
            self._artifact.setCurrentIndex(2)

    def apply_to(self, cfg: AppConfig) -> None:
        u = cfg.url
        u.crawl = self._crawl.isChecked()
        u.async_crawl = self._async_crawl.isChecked()
        u.crawl_depth = int(self._depth.value())
        u.max_pages = int(self._max_pages.value())
        u.download_linked_files = self._download.isChecked()
        u.obey_robots = self._robots.isChecked()
        u.same_site_only = self._same_site.isChecked()
        u.include_subdomains = self._subdomains.isChecked()
        u.crawl_delay_seconds = float(self._delay.value())
        u.timeout_seconds = float(self._timeout.value())
        u.max_response_bytes = int(self._max_mb.value()) * 1024 * 1024
        idx = self._artifact.currentIndex()
        u.artifact_layout_override = None if idx == 0 else (idx == 1)
