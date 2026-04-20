"""Output path existence / overwrite handling."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def prepare_output_path(path: Path, *, is_dir: bool, overwrite: bool) -> bool:
    """
    Ensure ``path`` can be written.

    Returns False if the caller should skip (exists and overwrite is False).
    """
    path = Path(path)
    if path.exists():
        if not overwrite:
            logger.warning("Skipping (exists, overwrite disabled): %s", path)
            return False
        if is_dir:
            shutil.rmtree(path, ignore_errors=False)
        else:
            path.unlink(missing_ok=True)
    if is_dir:
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    return True
