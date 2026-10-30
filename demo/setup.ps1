param([ValidateSet('auto','cpu','cu130')][string]$Compute = 'auto')
$ErrorActionPreference = 'Stop'
$demoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $demoRoot
$environmentPath = Join-Path $projectRoot '.venv-demo'
$pythonPath = Join-Path $environmentPath 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -3.11 -m venv $environmentPath }
    else { & python -m venv $environmentPath }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 is required. Install it, then run Setup again.' }
}
& $pythonPath -c "import sys; assert sys.version_info[:2] == (3, 11), 'Python 3.11 is required'"
if ($LASTEXITCODE -ne 0) { throw 'Use Python 3.11 for this demo environment.' }
if ($Compute -eq 'auto') {
    $Compute = 'cpu'
    if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
        $driverInfo = & nvidia-smi 2>$null | Out-String
        if ($driverInfo -match 'CUDA Version:\s*(\d+)\.(\d+)') {
            if ([int]$Matches[1] -ge 13) { $Compute = 'cu130' }
        }
    }
}
Write-Host "Preparing demo environment ($Compute). Existing research environments are unchanged."
& $pythonPath -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare pip in the demo environment.' }
& $pythonPath -m pip install --disable-pip-version-check -r (Join-Path $demoRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Could not install demo dependencies.' }
$torchIndex = if ($Compute -eq 'cu130') { 'https://download.pytorch.org/whl/cu130' } else { 'https://download.pytorch.org/whl/cpu' }
& $pythonPath -m pip install --disable-pip-version-check 'torch==2.14.0' --index-url $torchIndex
if ($LASTEXITCODE -ne 0) { throw 'Could not install PyTorch. Try .\demo\setup.ps1 -Compute cpu.' }
& $pythonPath -c "import torch; print('PyTorch:',torch.__version__); print('CUDA available:',torch.cuda.is_available())"
Write-Host 'Ready. Run Start-Dashboard.cmd (or demo/start.ps1).'
