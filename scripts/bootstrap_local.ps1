[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$secretDir = [System.IO.Path]::GetFullPath((Join-Path $repoRoot '.local\secrets'))
if (-not $secretDir.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to create secrets outside the repository"
}

New-Item -ItemType Directory -Path $secretDir -Force | Out-Null

function New-RandomHex {
    param([Parameter(Mandatory)][int]$Bytes)
    $buffer = New-Object byte[] $Bytes
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($buffer)
    }
    finally {
        $generator.Dispose()
    }
    return -join ($buffer | ForEach-Object { $_.ToString('x2') })
}

$values = [ordered]@{
    'postgres_password' = New-RandomHex -Bytes 24
    'minio_root_user' = 'ragcoreadmin'
    'minio_root_password' = New-RandomHex -Bytes 24
}

foreach ($entry in $values.GetEnumerator()) {
    $path = Join-Path $secretDir $entry.Key
    if (-not (Test-Path -LiteralPath $path)) {
        [System.IO.File]::WriteAllText($path, $entry.Value, [System.Text.Encoding]::ASCII)
        Write-Output "Created ignored local secret file: .local/secrets/$($entry.Key)"
    }
    else {
        Write-Output "Kept existing ignored local secret file: .local/secrets/$($entry.Key)"
    }
}

Write-Output 'Local Docker secret files are ready; values were not printed.'
