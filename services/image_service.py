"""Image OCR conversion."""

from __future__ import annotations

from pathlib import Path

from md_generator.image.convert_impl import (
    ConvertOptions as ImageConvertOptions,
    convert_image_paths,
    convert_images,
    convert_images_recursive,
)

from core.config_model import AppConfig, OcrStrategyUI
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_file


def _engines_tuple(cfg: AppConfig) -> tuple[str, ...]:
    engines = tuple(e.strip().lower() for e in cfg.image.engines if e.strip())
    if not engines:
        return ("tess",)
    if cfg.image.strategy == OcrStrategyUI.FAST:
        return (engines[0],)
    return engines


def _easy_langs(cfg: AppConfig) -> tuple[str, ...]:
    parts = [p.strip() for p in cfg.image.easy_langs_csv.split(",") if p.strip()]
    return tuple(parts) if parts else ("en",)


def run_image(src: Path, cfg: AppConfig, *, recursive: bool) -> Path:
    common = cfg.common
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    out_md = unique_output_file(out_root, stem, ".md", overwrite=common.overwrite)
    if not prepare_output_path(out_md, is_dir=False, overwrite=common.overwrite):
        raise FileExistsError(str(out_md))

    engines = _engines_tuple(cfg)
    strategy = "best"  # compare is multi-column; UI maps fast -> single engine
    opts = ImageConvertOptions(
        engines=engines,
        strategy=strategy,  # type: ignore[arg-type]
        title=cfg.image.title or "OCR",
        tess_lang=cfg.image.tess_lang,
        tesseract_cmd=cfg.image.tesseract_cmd or None,
        paddle_lang=cfg.image.paddle_lang,
        paddle_use_angle_cls=cfg.image.paddle_use_angle_cls,
        easy_langs=_easy_langs(cfg),
        verbose=common.verbose,
    )

    if src.is_file():
        convert_image_paths([Path(src)], out_md, opts)
    elif recursive:
        convert_images_recursive(Path(src), out_md, opts)
    else:
        convert_images(Path(src), out_md, opts)

    return out_md
