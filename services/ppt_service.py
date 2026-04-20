"""PowerPoint (.pptx) conversion."""

from __future__ import annotations

from pathlib import Path

from md_generator.ppt.convert_impl import convert_pptx
from md_generator.ppt.options import ConvertOptions as PptConvertOptions

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_dir, unique_output_file


def run_ppt(src: Path, cfg: AppConfig) -> Path:
    common = cfg.common
    p = cfg.ppt
    artifact = cfg.effective_artifact(for_ppt=True)
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    opts = PptConvertOptions(
        artifact_layout=artifact,
        verbose=common.verbose,
        extract_embedded_deep=p.extract_embedded_content,
    )

    if artifact:
        target_dir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
        if not prepare_output_path(target_dir, is_dir=True, overwrite=common.overwrite):
            raise FileExistsError(str(target_dir))
        convert_pptx(Path(src), target_dir, opts)
        return target_dir / "document.md"

    md_path = unique_output_file(out_root, stem, ".md", overwrite=common.overwrite)
    if not prepare_output_path(md_path, is_dir=False, overwrite=common.overwrite):
        raise FileExistsError(str(md_path))
    convert_pptx(Path(src), md_path, opts)
    return md_path
