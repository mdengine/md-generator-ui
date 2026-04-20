"""URL → Markdown conversion."""

from __future__ import annotations

import tempfile
from pathlib import Path

from md_generator.url.convert_impl import convert_url, convert_urls_from_list
from md_generator.url.fetch import fetch_html, new_client
from md_generator.url.options import ConvertOptions as UrlConvertOptions
from md_generator.url.page_convert import convert_one_page_artifact

from core.config_model import AppConfig
from services.output_ops import prepare_output_path
from utils.file_utils import unique_output_dir


def _url_options(cfg: AppConfig) -> UrlConvertOptions:
    u = cfg.url
    artifact = cfg.effective_artifact(for_url=True)
    return UrlConvertOptions(
        artifact_layout=artifact,
        verbose=cfg.common.verbose,
        crawl=u.crawl,
        max_depth=u.crawl_depth,
        max_pages=u.max_pages,
        download_linked_files=u.download_linked_files,
        crawl_delay_seconds=u.crawl_delay_seconds,
        async_crawl=u.async_crawl,
        obey_robots=u.obey_robots,
        same_site_only=u.same_site_only,
        include_subdomains=u.include_subdomains,
        timeout_seconds=u.timeout_seconds,
        max_response_bytes=u.max_response_bytes,
    )


def run_url_single(url: str, cfg: AppConfig) -> Path:
    common = cfg.common
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    opts = _url_options(cfg)
    artifact = opts.artifact_layout

    from md_generator.url.extract import url_to_slug

    if artifact:
        if opts.crawl:
            target = unique_output_dir(out_root, "crawl_bundle", overwrite=common.overwrite)
        else:
            target = unique_output_dir(out_root, url_to_slug(url, 1), overwrite=common.overwrite)
        if not prepare_output_path(target, is_dir=True, overwrite=common.overwrite):
            raise FileExistsError(str(target))
        convert_url(url.strip(), target, opts)
        return target / "document.md"

    md_path = _unique_md(out_root, url_to_slug(url, 1), common.overwrite)
    if not prepare_output_path(md_path, is_dir=False, overwrite=common.overwrite):
        raise FileExistsError(str(md_path))
    convert_url(url.strip(), md_path, opts)
    return md_path


def _unique_md(out_root: Path, stem: str, overwrite: bool) -> Path:
    from utils.file_utils import unique_output_file

    return unique_output_file(out_root, stem, ".md", overwrite=overwrite)


def run_url_list(urls: list[str], cfg: AppConfig) -> Path:
    common = cfg.common
    out_root = Path(common.output_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    opts = _url_options(cfg)
    parent = unique_output_dir(out_root, "url_batch", overwrite=common.overwrite)
    if not prepare_output_path(parent, is_dir=True, overwrite=common.overwrite):
        raise FileExistsError(str(parent))
    clean = [u.strip() for u in urls if u.strip()]
    convert_urls_from_list(clean, parent, opts)
    return parent / "document.md"


def preview_url_markdown(url: str, cfg: AppConfig, *, max_chars: int = 200_000) -> str:
    """Fetch and render first URL to Markdown text (uses temp artifact directory)."""
    u = cfg.url
    opts = UrlConvertOptions(
        artifact_layout=True,
        verbose=False,
        crawl=False,
        download_linked_files=u.download_linked_files,
        timeout_seconds=u.timeout_seconds,
        max_response_bytes=min(u.max_response_bytes, 5 * 1024 * 1024),
        table_csv=True,
    )
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "preview"
        root.mkdir(parents=True, exist_ok=True)
        with new_client(opts) as client:
            fr = fetch_html(url.strip(), client, opts)
            convert_one_page_artifact(fr.final_url, fr.text, root, opts, client)
        doc = root / "document.md"
        if not doc.is_file():
            return "(no document.md produced)"
        text = doc.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n… (truncated)"
        return text
