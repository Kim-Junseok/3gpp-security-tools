param(
    [string]$Python = "",
    [string]$Name = "3GPP-Security-Tools"
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
if (-not $Python) { $Python = Join-Path $ProjectRoot ".build/windows-python/python.exe" }
Push-Location $ProjectRoot
try {
    & $Python -c "import PyInstaller; assert PyInstaller.__version__ == '6.22.3', PyInstaller.__version__"
    if ($LASTEXITCODE -ne 0) { throw "Install the pinned packaging requirements first." }
    & $Python tools/write_build_info.py
    if ($LASTEXITCODE -ne 0) { throw "Build identity generation failed." }
    & $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name $Name --paths src --add-data "testdata;testdata" --add-data "build-info.json;." --distpath dist --workpath .build/pyinstaller packaging/launch.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }
    Get-FileHash (Join-Path $ProjectRoot "dist/$Name.exe") -Algorithm SHA256 | Format-List
} finally { Pop-Location }
