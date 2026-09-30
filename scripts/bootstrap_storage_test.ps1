[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$secretDir = [System.IO.Path]::GetFullPath((Join-Path $repoRoot '.local\secrets'))
if (-not $secretDir.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Refusing to create secrets outside repository'
}
New-Item -ItemType Directory -Path $secretDir -Force | Out-Null
foreach ($name in @('minio_reader_user', 'minio_uploader_user')) {
    $path = Join-Path $secretDir $name
    if (-not (Test-Path -LiteralPath $path)) {
        $value = if ($name -eq 'minio_reader_user') { 'ragcorereader' } else { 'ragcoreuploader' }
        [System.IO.File]::WriteAllText($path, $value, [System.Text.Encoding]::ASCII)
    }
}
foreach ($name in @('minio_reader_password', 'minio_uploader_password')) {
    $path = Join-Path $secretDir $name
    if (-not (Test-Path -LiteralPath $path)) {
        $bytes = New-Object byte[] 24
        $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
        $value = -join ($bytes | ForEach-Object { $_.ToString('x2') })
        [System.IO.File]::WriteAllText($path, $value, [System.Text.Encoding]::ASCII)
    }
}
Write-Output 'T11 ignored reader/uploader secret files ready; values not printed.'
