param([string]$Name = "3GPP-Security-Tools")
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$ReportDir = Join-Path $ProjectRoot "validation/v0.1/windows"
$TestRoot = Join-Path ([IO.Path]::GetTempPath()) ("3gpp-security-tools-" + [guid]::NewGuid().ToString("N"))
$LaunchDir = Join-Path $TestRoot "different-working-directory"
$BundleDir = Join-Path $TestRoot "portable"
$Runtime = Join-Path $ProjectRoot ".build/windows-python"
$HiddenRuntime = Join-Path $ProjectRoot ".build/windows-python-isolated"
$SavedEnv = @{}
$Renamed = $false
New-Item -ItemType Directory -Force $ReportDir,$LaunchDir,$BundleDir | Out-Null
$Exe = Join-Path $BundleDir "$Name.exe"
Copy-Item (Join-Path $ProjectRoot "dist/$Name.exe") $Exe
try {
    if (Test-Path $Runtime) {
        if (Test-Path $HiddenRuntime) { throw "An earlier isolated runtime already exists; restore it before testing." }
        Move-Item $Runtime $HiddenRuntime
        $Renamed = $true
    }
    foreach ($Key in @("PATH", "PYTHONHOME", "PYTHONPATH", "TCL_LIBRARY", "TK_LIBRARY")) {
        $SavedEnv[$Key] = [Environment]::GetEnvironmentVariable($Key, "Process")
        [Environment]::SetEnvironmentVariable($Key, $null, "Process")
    }
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
    $OfficialDir = Join-Path $TestRoot "official"
    $GuiReport = Join-Path $TestRoot "gui-report.json"
    $OfficialArgs = @("--validate", "--output", ('"' + $OfficialDir + '"'))
    $Process = Start-Process -FilePath $Exe -ArgumentList $OfficialArgs -WorkingDirectory $LaunchDir -Wait -PassThru
    if ($Process.ExitCode -ne 0) { throw "Packaged official tests failed with exit $($Process.ExitCode)" }
    $Official = Get-Content (Join-Path $OfficialDir "official-report.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Official.required -ne 36 -or $Official.passed -ne 36) { throw "Expected all 36 official cases." }
    $Process = Start-Process -FilePath $Exe -ArgumentList @("--gui-smoke-report", ('"' + $GuiReport + '"')) -WorkingDirectory $LaunchDir -Wait -PassThru
    if ($Process.ExitCode -ne 0) { throw "Packaged GUI tests failed with exit $($Process.ExitCode)" }
    $Gui = Get-Content $GuiReport -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Gui.total -lt 30 -or $Gui.passed -ne $Gui.total) { throw "GUI test report is incomplete or failed." }
    Copy-Item (Join-Path $OfficialDir "*.json") $ReportDir -Force
    Copy-Item $GuiReport (Join-Path $ReportDir "gui-report.json") -Force
    $Evidence = [ordered]@{
        category = "windows_portable_isolation"
        os = (Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture)
        exe_sha256 = (Get-FileHash $Exe -Algorithm SHA256).Hash.ToLower()
        copied_files = @(Get-ChildItem $BundleDir | Select-Object -ExpandProperty Name)
        working_directory = $LaunchDir
        development_runtime_renamed = $Renamed
        python_environment_cleared = $true
        path = $env:PATH
        official_required = $Official.required
        official_passed = $Official.passed
        gui_total = $Gui.total
        gui_passed = $Gui.passed
        scope = "Existing Windows 11 host with isolated development runtime; not a fresh VM or a Windows 10 test."
        test_directory = $TestRoot
    }
    $Evidence | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $ReportDir "deployment-report.json")
    Write-Output "Windows EXE: official $($Official.passed)/$($Official.required); GUI $($Gui.passed)/$($Gui.total)"
} finally {
    foreach ($Key in $SavedEnv.Keys) { [Environment]::SetEnvironmentVariable($Key, $SavedEnv[$Key], "Process") }
    if ($Renamed) { Move-Item $HiddenRuntime $Runtime }
}
