"""Aggregated application configuration (UI view model)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Literal


class InputMode(Enum):
    SINGLE_FILE = auto()
    MULTIPLE_FILES = auto()
    FOLDER = auto()
    URL = auto()


class OcrStrategyUI(Enum):
    BEST = "best"
    FAST = "fast"


@dataclass
class CommonSettings:
    output_dir: Path = field(default_factory=lambda: Path.home() / "md-generator-out")
    artifact_layout: bool = False
    verbose: bool = False
    overwrite: bool = True


@dataclass
class PdfSettings:
    extract_images: bool = True
    use_ocr: bool = False
    ocr_min_chars: int = 40


@dataclass
class WordSettings:
    """Word: custom images directory (relative name under output parent in classic mode)."""

    extract_images_dir: str = "images"
    page_break_as_hr: bool = True


@dataclass
class PptSettings:
    extract_embedded_content: bool = True
    artifact_layout_override: bool | None = None  # None = follow common.artifact_layout


@dataclass
class ExcelSettings:
    split_sheets: bool = False


@dataclass
class ImageOcrSettings:
    engines: tuple[str, ...] = ("tess", "paddle", "easy")
    strategy: OcrStrategyUI = OcrStrategyUI.BEST
    tess_lang: str = "eng"
    paddle_lang: str = "en"
    easy_langs_csv: str = "en"
    tesseract_cmd: str = ""
    paddle_use_angle_cls: bool = True
    title: str = "OCR"


@dataclass
class TextSettings:
    encoding: str = "utf-8"
    input_format: Literal["auto", "txt", "json", "xml"] = "auto"
    include_source_block: bool = True
    generate_toc: bool = False


@dataclass
class ZipSettings:
    nested_conversions: bool = True
    max_nested_depth: int = 16
    ocr_inside_zip: bool = False
    use_image_to_md: bool = True
    image_to_md_engines: str = "paddle,easy,tess"
    image_to_md_strategy: str = "best"


@dataclass
class UrlSettings:
    crawl_depth: int = 2
    max_pages: int = 30
    artifact_layout_override: bool | None = None
    download_linked_files: bool = True
    crawl: bool = False
    async_crawl: bool = False
    crawl_delay_seconds: float = 0.5
    obey_robots: bool = True
    same_site_only: bool = True
    include_subdomains: bool = True
    timeout_seconds: float = 30.0
    max_response_bytes: int = 10 * 1024 * 1024


@dataclass
class AppConfig:
    input_mode: InputMode = InputMode.SINGLE_FILE
    common: CommonSettings = field(default_factory=CommonSettings)
    pdf: PdfSettings = field(default_factory=PdfSettings)
    word: WordSettings = field(default_factory=WordSettings)
    ppt: PptSettings = field(default_factory=PptSettings)
    excel: ExcelSettings = field(default_factory=ExcelSettings)
    image: ImageOcrSettings = field(default_factory=ImageOcrSettings)
    text: TextSettings = field(default_factory=TextSettings)
    zip: ZipSettings = field(default_factory=ZipSettings)
    url: UrlSettings = field(default_factory=UrlSettings)

    def effective_artifact(self, for_ppt: bool = False, for_url: bool = False) -> bool:
        if for_ppt and self.ppt.artifact_layout_override is not None:
            return self.ppt.artifact_layout_override
        if for_url and self.url.artifact_layout_override is not None:
            return self.url.artifact_layout_override
        return self.common.artifact_layout
