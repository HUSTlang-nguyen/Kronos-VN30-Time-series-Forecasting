$ErrorActionPreference = "Stop"

$Repository = "https://github.com/shiyu-coder/Kronos.git"
$Revision = "67b630e67f6a18c9e9be918d9b4337c960db1e9a"
$Root = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $Root ".vendor\Kronos"

if (-not (Test-Path -LiteralPath (Join-Path $Target ".git"))) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
    git clone --filter=blob:none $Repository $Target
}

git -C $Target fetch --depth 1 origin $Revision
git -C $Target checkout --detach $Revision

$Resolved = git -C $Target rev-parse HEAD
if ($Resolved -ne $Revision) {
    throw "Kronos revision mismatch: expected $Revision, got $Resolved"
}

Write-Output "Kronos ready at $Target ($Resolved)"
