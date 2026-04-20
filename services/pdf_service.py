"""PDF conversion via md_generator."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from md_generator.pdf.pdf_extract import ConvertOptions as PdfConvertOptions, convert_pdf
from md_generator.pdf.utils import resolve_output

from core.config_model import AppConfig
from services.output_ops import prepare_output_path

logger = logging.getLogger(__name__)

_IMG_LINE = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$")


def _strip_image_lines(md_text: str) -> str:
    lines = md_text.splitlines()
    kept: list[str] = []
    for ln in lines:
        if _IMG_LINE.match(ln.strip()):
            continue
        kept.append(ln)
    return "\n".join(kept).strip() + "\n"


def _prune_unreferenced_images(md_path: Path, images_dir: Path) -> None:
    if not md_path.is_file() or not images_dir.is_dir():
        return
    text = md_path.read_text(encoding="utf-8", errors="replace")
    for f in images_dir.iterdir():
        if not f.is_file():
            continue
        rel = f.name
        if rel not in text:
            try:
                f.unlink()
            except OSError as e:
                logger.debug("Could not remove image %s: %s", f, e)


def run_pdf(src: Path, cfg: AppConfig) -> Path:
    from utils.file_utils import output_stem_for, unique_output_dir, unique_output_file

    common = cfg.common
    pdf_cfg = cfg.pdf
    artifact = common.artifact_layout
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    stem = output_stem_for(src)
    if artifact:
        target_dir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
        if not prepare_output_path(target_dir, is_dir=True, overwrite=common.overwrite):
            raise FileExistsError(str(target_dir))
        resolved = resolve_output(target_dir, artifact_layout=True, images_dir=None)
    else:
        md_path = unique_output_file(out_root, stem, ".md", overwrite=common.overwrite)
        if not prepare_output_path(md_path, is_dir=False, overwrite=common.overwrite):
            raise FileExistsError(str(md_path))
        resolved = resolve_output(md_path, artifact_layout=False, images_dir=None)

    opts = PdfConvertOptions(
        use_ocr=pdf_cfg.use_ocr,
        ocr_min_chars=pdf_cfg.ocr_min_chars,
        verbose=common.verbose,
    )
    convert_pdf(Path(src), resolved, opts)

    md_path = Path(resolved.markdown_path)
    img_dir = Path(resolved.images_dir)

    if not pdf_cfg.extract_images:
        body = md_path.read_text(encoding="utf-8", errors="replace")
        new_body = _strip_image_lines(body)
        md_path.write_text(new_body, encoding="utf-8", newline="\n")
        _prune_unreferenced_images(md_path, img_dir)

    return md_path if not artifact else md_path.parent
