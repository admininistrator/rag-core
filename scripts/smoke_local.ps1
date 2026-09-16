[CmdletBinding()]
param(
    [int]$ApiPort = 8000
)

$ErrorActionPreference = 'Stop'
$baseUrl = "http://127.0.0.1:$ApiPort"
$live = Invoke-RestMethod -Uri "$baseUrl/health/live" -TimeoutSec 10
$ready = Invoke-RestMethod -Uri "$baseUrl/health/ready" -TimeoutSec 10

if ($live.status -ne 'ok') {
    throw "Liveness status was not ok"
}
if ($ready.status -ne 'ready') {
    throw "Readiness status was not ready"
}
foreach ($name in @('postgres', 'redis', 'qdrant')) {
    if ($ready.components.$name -ne 'ok') {
        throw "Readiness component $name was not ok"
    }
}

Write-Output 'PASS /health/live status=ok'
Write-Output 'PASS /health/ready status=ready components=postgres,redis,qdrant'
