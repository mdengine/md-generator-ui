"""ZIP archive conversion (artifact layout required by mdengine)."""

from __future__ import annotations

from pathlib import Path

from md_generator.archive.convert_impl import convert_zip
from md_generator.archive.options import ConvertOptions as ZipConvertOptions

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_dir


def run_zip(src: Path, cfg: AppConfig) -> Path:
    common = cfg.common
    z = cfg.zip
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    target_dir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
    if not prepare_output_path(target_dir, is_dir=True, overwrite=common.overwrite):
        raise FileExistsError(str(target_dir))

    opts = ZipConvertOptions(
        verbose=common.verbose,
        artifact_layout=True,
        expand_nested_zips=z.nested_conversions,
        max_nested_zip_depth=z.max_nested_depth,
        image_ocr=z.ocr_inside_zip,
        pdf_ocr=z.ocr_inside_zip,
        use_image_to_md=z.use_image_to_md,
        image_to_md_engines=z.image_to_md_engines,
        image_to_md_strategy=z.image_to_md_strategy,
    )
    convert_zip(Path(src), target_dir, opts)
    return target_dir / "document.md"
