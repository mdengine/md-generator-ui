"""File discovery, type routing, and safe output paths."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from enum import Enum, auto
from pathlib import Path


class ConversionKind(Enum):
    PDF = auto()
    WORD = auto()
    PPT = auto()
    EXCEL = auto()
    IMAGE = auto()
    TEXT = auto()
    ZIP = auto()
    URL = auto()
    UNKNOWN = auto()


PDF_EXT = {".pdf"}
WORD_EXT = {".docx"}
PPT_EXT = {".pptx"}
EXCEL_EXT = {".xlsx", ".xlsm", ".csv"}
TEXT_EXT = {".txt", ".json", ".xml"}
ZIP_EXT = {".zip"}
IMAGE_EXT = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}


def classify_path(path: Path) -> ConversionKind:
    suf = path.suffix.casefold()
    if suf in PDF_EXT:
        return ConversionKind.PDF
    if suf in WORD_EXT:
        return ConversionKind.WORD
    if suf in PPT_EXT:
        return ConversionKind.PPT
    if suf in EXCEL_EXT:
        return ConversionKind.EXCEL
    if suf in TEXT_EXT:
        return ConversionKind.TEXT
    if suf in ZIP_EXT:
        return ConversionKind.ZIP
    if suf in IMAGE_EXT:
        return ConversionKind.IMAGE
    return ConversionKind.UNKNOWN


def iter_files_recursive(root: Path, *, follow_symlinks: bool = False) -> list[Path]:
    root = root.resolve()
    if root.is_file():
        return [root]
    out: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            if not follow_symlinks and p.is_symlink():
                continue
            out.append(p)
    return sorted(out)


_SLUG_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def output_stem_for(path: Path) -> str:
    """Human-readable stem plus short hash so different paths with the same filename do not clash."""
    base = slugify_filename(path.stem)
    digest = hashlib.sha1(str(path.resolve()).encode("utf-8", errors="replace")).hexdigest()[:8]
    return f"{base}_{digest}"


def slugify_filename(stem: str, max_len: int = 120) -> str:
    s = unicodedata.normalize("NFKD", stem)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = _SLUG_RE.sub("_", s).strip("._") or "output"
    return s[:max_len]


def unique_output_dir(parent: Path, stem: str, *, overwrite: bool) -> Path:
    """Return a directory `parent / slug` or `parent / slug_N` if exists and not overwrite."""
    base = slugify_filename(stem)
    candidate = parent / base
    if overwrite or not candidate.exists():
        return candidate
    n = 2
    while True:
        c = parent / f"{base}_{n}"
        if not c.exists():
            return c
        n += 1


def unique_output_file(parent: Path, stem: str, suffix: str, *, overwrite: bool) -> Path:
    base = slugify_filename(stem)
    candidate = parent / f"{base}{suffix}"
    if overwrite or not candidate.is_file():
        return candidate
    n = 2
    while True:
        c = parent / f"{base}_{n}{suffix}"
        if not c.is_file():
            return c
        n += 1


def collect_batch_files(paths: list[Path], *, recursive_dirs: bool) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_dir() and recursive_dirs:
            files.extend(iter_files_recursive(p))
        elif p.is_file():
            files.append(p.resolve())
        elif p.is_dir():
            files.extend(iter_files_recursive(p))
    # de-dupe preserve order
    seen: set[Path] = set()
    uniq: list[Path] = []
    for f in files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return uniq
