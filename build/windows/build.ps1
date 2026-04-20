$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    python -m pip install -r requirements-dev.txt
}

# Equivalent to: pyinstaller --onefile --windowed --name md-generator-ui app.py
# (uses md-generator-ui.spec for hiddenimports / md_generator)
pyinstaller --noconfirm md-generator-ui.spec

Write-Host "Done. Output: $Root\dist\md-generator-ui.exe"
