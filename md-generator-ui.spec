# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for md-generator-ui (one-file windowed GUI).

Avoid collect_submodules('md_generator'): it pulls optional heavy stacks (torch, etc.)
via lazy imports. Expand this list if a runtime ImportError appears in the frozen exe.
"""

block_cipher = None

hiddenimports = [
    "md_generator",
    "md_generator.pdf",
    "md_generator.pdf.pdf_extract",
    "md_generator.pdf.utils",
    "md_generator.word",
    "md_generator.word.converter",
    "md_generator.word.api.convert_util",
    "md_generator.word.artifact",
    "md_generator.ppt",
    "md_generator.ppt.convert_impl",
    "md_generator.ppt.options",
    "md_generator.xlsx",
    "md_generator.xlsx.converter_core",
    "md_generator.xlsx.convert_config",
    "md_generator.image",
    "md_generator.image.convert_impl",
    "md_generator.image.backends.tesseract",
    "md_generator.image.backends.paddle",
    "md_generator.image.backends.easy",
    "md_generator.text",
    "md_generator.text.convert_impl",
    "md_generator.text.options",
    "md_generator.archive",
    "md_generator.archive.convert_impl",
    "md_generator.archive.options",
    "md_generator.url",
    "md_generator.url.convert_impl",
    "md_generator.url.options",
    "md_generator.url.fetch",
    "md_generator.url.page_convert",
    "md_generator.url.html_to_md",
    "md_generator.url.extract",
    "md_generator.url.crawl",
    "fitz",
    "pdfplumber",
    "mammoth",
    "markdownify",
    "pptx",
    "openpyxl",
    "PIL",
    "PIL.Image",
    "httpx",
    "bs4",
    "lxml",
    "lxml.html",
    "readability",
    "readability.readability",
    "pytesseract",
]

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="md-generator-ui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
