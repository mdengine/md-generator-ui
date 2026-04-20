"""Plain text / JSON / XML conversion."""

from __future__ import annotations

from pathlib import Path

from md_generator.text.convert_impl import convert_text_file
from md_generator.text.options import ConvertOptions as TextConvertOptions

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import output_stem_for, unique_output_dir, unique_output_file


def run_text(src: Path, cfg: AppConfig) -> Path:
    common = cfg.common
    t = cfg.text
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stem = output_stem_for(src)

    opts = TextConvertOptions(
        artifact_layout=common.artifact_layout,
        verbose=common.verbose,
        encoding=t.encoding,
        input_format=t.input_format,
        include_source_block=t.include_source_block,
        generate_toc=t.generate_toc,
    )

    if common.artifact_layout:
        target_dir = unique_output_dir(out_root, stem, overwrite=common.overwrite)
        if not prepare_output_path(target_dir, is_dir=True, overwrite=common.overwrite):
            raise FileExistsError(str(target_dir))
        convert_text_file(Path(src), target_dir, opts)
        return target_dir / "document.md"

    md_path = unique_output_file(out_root, stem, ".md", overwrite=common.overwrite)
    if not prepare_output_path(md_path, is_dir=False, overwrite=common.overwrite):
        raise FileExistsError(str(md_path))
    convert_text_file(Path(src), md_path, opts)
    return md_path
