param([switch]$Cpu, [int]$Port = 8000, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonPath = Join-Path $projectRoot '.venv-demo/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { & (Join-Path $projectRoot 'demo/setup.ps1') }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'demo/frontend/dist/index.html'))) { throw 'Frontend is not built. Use the dashboard ZIP, or build demo/frontend first.' }
$address = "http://127.0.0.1:$Port"
try {
    $existing = Invoke-RestMethod "$address/api/health" -TimeoutSec 2
    if ($existing.app -eq 'vn30-inference-studio') {
        if (-not $NoBrowser) { Start-Process $address }
        Write-Host "Dashboard is already running at $address"
        return
    }
} catch { }
$launchArgs = @('-m','demo.run','--port',"$Port")
if ($Cpu) { $launchArgs += '--cpu' }
if (-not $NoBrowser) { $launchArgs += '--open-browser' }
Push-Location $projectRoot
try { & $pythonPath @launchArgs } finally { Pop-Location }
