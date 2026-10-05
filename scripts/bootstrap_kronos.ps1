$ErrorActionPreference = "Stop"

# Compatibility entry point; pinned revision and checkout checks live in Python.
$Root = Split-Path -Parent $PSScriptRoot
$PythonExecutable = Join-Path $Root ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $PythonExecutable)) {
    throw "Run uv sync --frozen --group dev before bootstrapping Kronos"
}
& $PythonExecutable (Join-Path $PSScriptRoot "bootstrap_kronos.py")
exit $LASTEXITCODE
