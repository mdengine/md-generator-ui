# md-generator-ui

Cross-platform desktop UI for [mdengine](https://pypi.org/project/mdengine/) (`import md_generator`): convert PDF, Word, PowerPoint, Excel, images (OCR), text/JSON/XML, ZIP archives, and URLs to Markdown.

## Requirements

- Python 3.10 or newer
- Optional: [Tesseract](https://github.com/tesseract-ocr/tesseract) on `PATH` for Tesseract OCR

## Run locally

```powershell
cd md-generator-ui
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

macOS / Linux:

```bash
cd md-generator-ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

If the pinned `mdengine` version is not yet on PyPI, temporarily edit `requirements.txt` to install from your clone:

```bash
pip install -e "C:/path/to/md-generator[pdf,word,ppt,xlsx,image-ocr,archive,url-full]"
pip install PySide6
```

## Build (one-file GUI; no Python needed on target machine)

Windows:

```powershell
pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File build/windows/build.ps1
```

Linux:

```bash
pip install -r requirements-dev.txt
bash build/linux/build.sh
```

macOS:

```bash
pip install -r requirements-dev.txt
bash build/mac/build.sh
```

Artifacts appear under `dist/`.

The first PyInstaller run can take a long time and produce a very large executable because optional OCR stacks (Paddle/EasyOCR) pull many native wheels. If you only need Tesseract, consider installing `mdengine` without the `image-ocr` extra in a dedicated venv before building, then adjust `requirements.txt` accordingly.

### 32-bit builds

Best-effort only: install 32-bit Python and matching wheels; many OCR stacks do not publish win32 wheels. Prefer x64.

### User vs system install

- **User**: `pip install --user -r requirements.txt` (scripts in your user profile).
- **System**: elevated `pip install` or use the generated installer (Inno Setup / `.deb` / `.dmg`) for end users.

## Optional installers

- Windows: edit and compile `build/windows/installer.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) after a PyInstaller build.
- Linux: see `build/linux/make_deb.sh` and `build/linux/deb/`.
- macOS: `bash build/mac/make_dmg.sh` (optional `create-dmg`).

## License

MIT (same spirit as mdengine); see repository root when a `LICENSE` file is added.
