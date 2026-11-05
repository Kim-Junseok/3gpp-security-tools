param([string]$Name = "3GPP-Security-Tools", [switch]$DeveloperRuntimeAlreadyIsolated,
      [string]$ReportDirectory = "validation/256-bit/windows",
      [int]$ExpectedOfficial = 135, [int]$ExpectedGui = 201)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$ReportDir = Join-Path $ProjectRoot $ReportDirectory
$TestRoot = Join-Path ([IO.Path]::GetTempPath()) ("3gpp-security-tools-" + [guid]::NewGuid().ToString("N"))
$LaunchDir = Join-Path $TestRoot "different-working-directory"
$BundleDir = Join-Path $TestRoot "portable"
$Runtime = Join-Path $ProjectRoot ".build/windows-python"
$SavedEnv = @{}
$Renamed = [bool]$DeveloperRuntimeAlreadyIsolated
if ($Renamed -and (Test-Path $Runtime)) { throw "Developer runtime is still accessible at its build path." }
New-Item -ItemType Directory -Force $ReportDir,$LaunchDir,$BundleDir | Out-Null
$Exe = Join-Path $BundleDir "$Name.exe"
Copy-Item (Join-Path $ProjectRoot "dist/$Name.exe") $Exe
try {
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
    if ($Official.required -ne $ExpectedOfficial -or $Official.passed -ne $ExpectedOfficial) { throw "Expected all $ExpectedOfficial official cases." }
    $Process = Start-Process -FilePath $Exe -ArgumentList @("--gui-smoke-report", ('"' + $GuiReport + '"')) -WorkingDirectory $LaunchDir -Wait -PassThru
    if ($Process.ExitCode -ne 0) { throw "Packaged GUI tests failed with exit $($Process.ExitCode)" }
    $Gui = Get-Content $GuiReport -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Gui.total -ne $ExpectedGui -or $Gui.passed -ne $Gui.total) { throw "Expected all $ExpectedGui GUI cases." }
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
        scope = "Windows x64 host; standalone EXE copied alone and run from a different directory with Python/Tcl/Tk environment and PATH cleared. Other installed runtimes have not necessarily been removed."
        test_directory = $TestRoot
    }
    $Evidence | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $ReportDir "deployment-report.json")
    Write-Output "Windows EXE: official $($Official.passed)/$($Official.required); GUI $($Gui.passed)/$($Gui.total)"
} finally {
    foreach ($Key in $SavedEnv.Keys) { [Environment]::SetEnvironmentVariable($Key, $SavedEnv[$Key], "Process") }
}
