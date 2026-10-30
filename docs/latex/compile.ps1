param([string]$Tectonic)
$ErrorActionPreference = 'Stop'

if (-not $Tectonic) {
    $installed = Get-Command tectonic -ErrorAction SilentlyContinue
    if ($installed) {
        $Tectonic = $installed.Source
    } else {
        $portable = Join-Path $PSScriptRoot '../../.cache/tectonic/tectonic.exe'
        if (Test-Path -LiteralPath $portable) {
            $Tectonic = (Resolve-Path -LiteralPath $portable).Path
        } else {
            throw 'Cần Tectonic trong PATH hoặc tham số -Tectonic. Có thể upload ZIP lên Overleaf và chọn XeLaTeX.'
        }
    }
}
$engine = (Resolve-Path -LiteralPath $Tectonic).Path
$build = Join-Path $PSScriptRoot '.build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
Push-Location $PSScriptRoot
try {
    & $engine --keep-logs --outdir $build main.tex
    if ($LASTEXITCODE -ne 0) { throw "Biên dịch lỗi: $LASTEXITCODE" }
    $pdf = Join-Path $build 'main.pdf'
    if (-not (Test-Path -LiteralPath $pdf)) { throw 'Không tìm thấy PDF sau biên dịch.' }
    Copy-Item -LiteralPath $pdf -Destination (Join-Path $PSScriptRoot 'VN30_Report.pdf') -Force
    Write-Host 'Đã tạo VN30_Report.pdf'
} finally {
    Pop-Location
}
