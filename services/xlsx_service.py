"""Excel / CSV conversion."""

from __future__ import annotations

from pathlib import Path

from md_generator.xlsx.converter_core import convert_excel_to_markdown

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_dir


def run_excel(src: Path, cfg: AppConfig) -> Path:
    common = cfg.common
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    out_dir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
    if not prepare_output_path(out_dir, is_dir=True, overwrite=common.overwrite):
        raise FileExistsError(str(out_dir))

    convert_excel_to_markdown(
        Path(src),
        out_dir,
        split_by_sheet=cfg.excel.split_sheets,
    )
    # When split_by_sheet, multiple files; return directory as primary result
    return out_dir
