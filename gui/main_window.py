"""Primary application window."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QCloseEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.config_model import AppConfig, InputMode
from core.task_manager import ConversionThread
from gui.components.common_panel import CommonPanel
from gui.tabs.excel_tab import ExcelTab
from gui.tabs.image_tab import ImageTab
from gui.tabs.pdf_tab import PdfTab
from gui.tabs.ppt_tab import PptTab
from gui.tabs.text_tab import TextTab
from gui.tabs.url_tab import UrlTab
from gui.tabs.word_tab import WordTab
from gui.tabs.zip_tab import ZipTab
from gui.url_preview_thread import UrlPreviewThread
from utils.logger import QtLogEmitter, setup_root_logger

logger = logging.getLogger(__name__)


class _LogBridge(QObject):
    line = Signal(str)


class DropList(QListWidget):
    """List widget accepting file/folder drops."""

    paths_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:  # noqa: N802
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:  # noqa: N802
        if not e.mimeData().hasUrls():
            super().dropEvent(e)
            return
        for u in e.mimeData().urls():
            p = Path(u.toLocalFile())
            if p.exists():
                self.add_path(p)
        self.paths_changed.emit()
        e.acceptProposedAction()

    def add_path(self, p: Path) -> None:
        s = str(p.resolve())
        for i in range(self.count()):
            if self.item(i).text() == s:
                return
        self.addItem(s)

    def paths(self) -> list[Path]:
        return [Path(self.item(i).text()) for i in range(self.count())]

    def set_paths(self, paths: list[Path]) -> None:
        self.clear()
        for p in paths:
            self.add_path(p)


class MainWindow(QWidget):
    """Main window (QWidget so PyInstaller --windowed works without QMainWindow menu requirements)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("md-generator-ui")
        self.resize(1280, 780)

        self._cfg = AppConfig()

        self._log_bridge = _LogBridge()
        self._log_emitter = QtLogEmitter(self._log_bridge.line)
        self._log_handler = setup_root_logger(verbose=False, qt_emitter=self._log_emitter)
        self._log_bridge.line.connect(self._append_log)

        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._log_emitter.flush_pending)
        self._log_timer.start(120)

        # --- Left: input ---
        left = QVBoxLayout()
        mode_box = QVBoxLayout()
        self._mode_single = QRadioButton("Single file")
        self._mode_multi = QRadioButton("Multiple files")
        self._mode_folder = QRadioButton("Folder (recursive)")
        self._mode_url = QRadioButton("URL extraction")
        self._mode_single.setChecked(True)
        grp = QButtonGroup(self)
        for i, w in enumerate((self._mode_single, self._mode_multi, self._mode_folder, self._mode_url)):
            grp.addButton(w, i)
        for w in (self._mode_single, self._mode_multi, self._mode_folder, self._mode_url):
            mode_box.addWidget(w)
        grp.idClicked.connect(self._on_mode_id)

        self._stack = QStackedWidget()
        file_page = QWidget()
        fp_lay = QVBoxLayout(file_page)
        self._list = DropList()
        self._list.paths_changed.connect(self._refresh_mode_hint)
        fp_lay.addWidget(QLabel("Queue (drag && drop files or folders):"))
        fp_lay.addWidget(self._list, 1)
        btn_row = QHBoxLayout()
        add_f = QPushButton("Add files…")
        add_f.clicked.connect(self._add_files)
        add_d = QPushButton("Add folder…")
        add_d.clicked.connect(self._add_folder)
        clr = QPushButton("Clear")
        clr.clicked.connect(self._list.clear)
        btn_row.addWidget(add_f)
        btn_row.addWidget(add_d)
        btn_row.addWidget(clr)
        fp_lay.addLayout(btn_row)

        url_page = QWidget()
        url_lay = QVBoxLayout(url_page)
        url_lay.addWidget(QLabel("Enter URLs in the URL tab center panel, or paste here:"))
        self._url_quick = QPlainTextEdit()
        self._url_quick.setMaximumHeight(120)
        self._url_quick.setPlaceholderText("https://example.com …")
        url_lay.addWidget(self._url_quick)

        self._stack.addWidget(file_page)
        self._stack.addWidget(url_page)

        left.addLayout(mode_box)
        left.addWidget(self._stack)

        # --- Center: common + tabs ---
        center = QVBoxLayout()
        self._common = CommonPanel()
        self._tabw = QTabWidget()
        self._pdf = PdfTab()
        self._word = WordTab()
        self._ppt = PptTab()
        self._xlsx = ExcelTab()
        self._img = ImageTab()
        self._txt = TextTab()
        self._zip = ZipTab()
        self._url = UrlTab()
        for label, w in (
            ("PDF", self._pdf),
            ("Word", self._word),
            ("PPT", self._ppt),
            ("Excel", self._xlsx),
            ("Image OCR", self._img),
            ("Text", self._txt),
            ("ZIP", self._zip),
            ("URL", self._url),
        ):
            self._tabw.addTab(w, label)
        center.addWidget(self._common)
        center.addWidget(self._tabw, 1)

        # --- Right: log + progress ---
        right = QVBoxLayout()
        self._progress = QProgressBar()
        self._progress.setRange(0, 1)
        self._progress.setValue(0)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setObjectName("logPanel")
        right.addWidget(QLabel("Logs"))
        right.addWidget(self._progress)
        right.addWidget(self._log, 1)

        # --- Bottom buttons ---
        bottom = QHBoxLayout()
        self._start = QPushButton("Start")
        self._start.clicked.connect(self._on_start)
        self._cancel = QPushButton("Cancel")
        self._cancel.setEnabled(False)
        self._cancel.clicked.connect(self._on_cancel)
        bottom.addStretch(1)
        bottom.addWidget(self._start)
        bottom.addWidget(self._cancel)

        splitter = QSplitter(Qt.Horizontal)
        left_w = QWidget()
        left_w.setLayout(left)
        center_w = QWidget()
        center_w.setLayout(center)
        right_w = QWidget()
        right_w.setLayout(right)
        splitter.addWidget(left_w)
        splitter.addWidget(center_w)
        splitter.addWidget(right_w)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)

        outer = QVBoxLayout()
        outer.addWidget(splitter, 1)
        outer.addLayout(bottom)
        self.setLayout(outer)

        self._thread: ConversionThread | None = None
        self._preview_thread: UrlPreviewThread | None = None

        self._url.preview_requested.connect(self._on_preview_url)
        self._load_all_from_cfg()
        self._on_mode_id(0)

    def _load_all_from_cfg(self) -> None:
        self._common.load_from(self._cfg)
        self._pdf.load_from(self._cfg)
        self._word.load_from(self._cfg)
        self._ppt.load_from(self._cfg)
        self._xlsx.load_from(self._cfg)
        self._img.load_from(self._cfg)
        self._txt.load_from(self._cfg)
        self._zip.load_from(self._cfg)
        self._url.load_from(self._cfg)

    def _sync_all_to_cfg(self) -> None:
        self._common.apply_to(self._cfg)
        self._pdf.apply_to(self._cfg)
        self._word.apply_to(self._cfg)
        self._ppt.apply_to(self._cfg)
        self._xlsx.apply_to(self._cfg)
        self._img.apply_to(self._cfg)
        self._txt.apply_to(self._cfg)
        self._zip.apply_to(self._cfg)
        self._url.apply_to(self._cfg)

    def _on_mode_id(self, idx: int) -> None:
        mapping = {
            0: InputMode.SINGLE_FILE,
            1: InputMode.MULTIPLE_FILES,
            2: InputMode.FOLDER,
            3: InputMode.URL,
        }
        self._cfg.input_mode = mapping.get(idx, InputMode.SINGLE_FILE)
        self._stack.setCurrentIndex(1 if self._cfg.input_mode == InputMode.URL else 0)
        self._refresh_mode_hint()

    def _refresh_mode_hint(self) -> None:
        """Reserved for future status hints (queue count, mode warnings)."""
        return

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select files", str(Path.home()))
        for f in files:
            self._list.add_path(Path(f))
        self._list.paths_changed.emit()

    def _add_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select folder", str(Path.home()))
        if d:
            self._list.add_path(Path(d))
            self._list.paths_changed.emit()

    def _append_log(self, line: str) -> None:
        self._log.appendPlainText(line)

    def _on_start(self) -> None:
        if self._thread and self._thread.isRunning():
            QMessageBox.information(self, "Busy", "A conversion is already running.")
            return
        self._sync_all_to_cfg()
        logging.getLogger().setLevel(logging.DEBUG if self._cfg.common.verbose else logging.INFO)

        paths = self._list.paths()
        urls_text = self._url.urls_text().strip() or self._url_quick.toPlainText().strip()
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

        if self._cfg.input_mode == InputMode.URL:
            if not urls:
                QMessageBox.warning(self, "URLs", "Add at least one URL (URL tab or quick paste).")
                return
        else:
            if not paths:
                QMessageBox.warning(self, "Inputs", "Add at least one file or folder.")
                return
            if self._cfg.input_mode == InputMode.SINGLE_FILE and len(paths) != 1:
                QMessageBox.warning(self, "Single file", "Select exactly one item in the queue for single-file mode.")
                return

        self._log.clear()
        self._start.setEnabled(False)
        self._cancel.setEnabled(True)

        self._thread = ConversionThread(self._cfg, paths, urls, self)
        self._thread.log_line.connect(self._append_log)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.start()

    def _on_progress(self, cur: int, total: int) -> None:
        self._progress.setMaximum(max(1, total))
        self._progress.setValue(cur)

    def _on_thread_finished(self, ok: bool, msg: str) -> None:
        self._start.setEnabled(True)
        self._cancel.setEnabled(False)
        self._append_log(msg)
        if not ok and msg not in ("Cancelled",):
            QMessageBox.warning(self, "Conversion", msg)

    def _on_cancel(self) -> None:
        if self._thread and self._thread.isRunning():
            self._thread.request_cancel()
            self._append_log("Cancel requested…")

    def _on_preview_url(self) -> None:
        if self._preview_thread and self._preview_thread.isRunning():
            QMessageBox.information(self, "Busy", "Preview already running.")
            return
        self._sync_all_to_cfg()
        urls_text = self._url.urls_text().strip() or self._url_quick.toPlainText().strip()
        lines = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not lines:
            QMessageBox.warning(self, "Preview", "Enter a URL in the URL tab.")
            return
        first = lines[0]
        self._append_log(f"Preview fetch: {first}")
        self._preview_thread = UrlPreviewThread(first, self._cfg, self)
        self._preview_thread.preview_ok.connect(self._on_preview_ok)
        self._preview_thread.preview_failed.connect(self._on_preview_fail)
        self._preview_thread.start()

    def _on_preview_ok(self, text: str) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("URL preview — Markdown")
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Read-only preview of converted Markdown:"))
        te = QPlainTextEdit()
        te.setReadOnly(True)
        te.setPlainText(text)
        lay.addWidget(te)
        close = QPushButton("Close")
        close.clicked.connect(dlg.accept)
        lay.addWidget(close)
        dlg.resize(760, 560)
        dlg.exec()

    def _on_preview_fail(self, err: str) -> None:
        QMessageBox.critical(self, "Preview failed", err)
        self._append_log(f"Preview error: {err}")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._thread and self._thread.isRunning():
            self._thread.request_cancel()
            self._thread.wait(3000)
        super().closeEvent(event)
