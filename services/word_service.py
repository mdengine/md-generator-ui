"""Word (.docx) conversion."""

from __future__ import annotations

from pathlib import Path

from md_generator.word.api.convert_util import convert_upload_to_artifact_dir
from md_generator.word.converter import convert_docx_to_markdown

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_dir, unique_output_file


def run_word(src: Path, cfg: AppConfig) -> Path:
    common = cfg.common
    w = cfg.word
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    if common.artifact_layout:
        workdir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
        if not prepare_output_path(workdir, is_dir=True, overwrite=common.overwrite):
            raise FileExistsError(str(workdir))
        convert_upload_to_artifact_dir(
            Path(src),
            workdir,
            page_break_as_hr=w.page_break_as_hr,
        )
        return workdir / "document.md"

    md_path = unique_output_file(out_root, stem, ".md", overwrite=common.overwrite)
    if not prepare_output_path(md_path, is_dir=False, overwrite=common.overwrite):
        raise FileExistsError(str(md_path))
    images_dir = (md_path.parent / w.extract_images_dir).resolve()
    convert_docx_to_markdown(
        Path(src),
        md_path,
        images_dir=images_dir,
        page_break_as_hr=w.page_break_as_hr,
        verbose=common.verbose,
    )
    return md_path
