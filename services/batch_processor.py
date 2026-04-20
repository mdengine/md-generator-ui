"""Build queues and dispatch conversions."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from core.config_model import AppConfig, InputMode
from services import (
    image_service,
    pdf_service,
    ppt_service,
    text_service,
    url_service,
    word_service,
    xlsx_service,
    zip_service,
)
from utils.file_utils import ConversionKind, classify_path, collect_batch_files

logger = logging.getLogger(__name__)


@dataclass
class BatchItem:
    """One unit of work."""

    kind: ConversionKind
    path: Path | None = None
    url: str | None = None
    urls: list[str] | None = None  # multi-URL single job


def build_items_from_paths(paths: list[Path], *, input_mode: InputMode) -> list[BatchItem]:
    recursive = input_mode == InputMode.FOLDER
    files = collect_batch_files(paths, recursive_dirs=recursive)
    items: list[BatchItem] = []
    for f in files:
        k = classify_path(f)
        if k == ConversionKind.UNKNOWN:
            logger.warning("Skip unsupported file type: %s", f)
            continue
        items.append(BatchItem(kind=k, path=f))
    return items


def build_items_from_urls(urls: list[str]) -> list[BatchItem]:
    clean = [u.strip() for u in urls if u.strip()]
    if not clean:
        return []
    if len(clean) == 1:
        return [BatchItem(kind=ConversionKind.URL, url=clean[0])]
    return [BatchItem(kind=ConversionKind.URL, urls=clean)]


def process_item(
    item: BatchItem,
    cfg: AppConfig,
    *,
    cancel: threading.Event,
) -> Path:
    if cancel.is_set():
        raise RuntimeError("Cancelled")

    if item.kind == ConversionKind.URL:
        if cancel.is_set():
            raise RuntimeError("Cancelled")
        if item.urls:
            return url_service.run_url_list(item.urls, cfg)
        if item.url:
            return url_service.run_url_single(item.url, cfg)
        raise ValueError("URL batch item missing url(s)")

    assert item.path is not None
    src = item.path

    if item.kind == ConversionKind.PDF:
        return pdf_service.run_pdf(src, cfg)
    if item.kind == ConversionKind.WORD:
        return word_service.run_word(src, cfg)
    if item.kind == ConversionKind.PPT:
        return ppt_service.run_ppt(src, cfg)
    if item.kind == ConversionKind.EXCEL:
        return xlsx_service.run_excel(src, cfg)
    if item.kind == ConversionKind.IMAGE:
        recursive = cfg.input_mode == InputMode.FOLDER and src.is_dir()
        return image_service.run_image(src, cfg, recursive=recursive)
    if item.kind == ConversionKind.TEXT:
        return text_service.run_text(src, cfg)
    if item.kind == ConversionKind.ZIP:
        return zip_service.run_zip(src, cfg)

    raise ValueError(f"Unsupported batch item: {item}")
