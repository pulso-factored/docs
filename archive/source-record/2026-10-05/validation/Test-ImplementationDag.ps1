$ErrorActionPreference = 'Stop'
$specPath = Join-Path $PSScriptRoot '..\TECH_SPEC_PULSO_AUTOMEJORA_V2.md'
$specLines = Get-Content -LiteralPath $specPath
$units = @{}
$insideCatalog = $false
foreach ($specLine in $specLines) {
  if ($specLine -match '^### 30\.8 ') { $insideCatalog = $true; continue }
  if ($specLine -match '^### 30\.9 ') { $insideCatalog = $false }
  if ($insideCatalog -and $specLine -match '^\| (U\d{2}(?:-[A-Z]+)?) ') {
    $unitId = $Matches[1]
    if ($units.ContainsKey($unitId)) { throw "Duplicate unit $unitId" }
    $cells = [regex]::Split($specLine, '(?<!\\)\|')
    if ($cells.Count -ne 6) { throw "Unexpected columns for $unitId" }
    $deps = @([regex]::Matches($cells[3], 'U\d{2}(?:-[A-Z]+)?') | ForEach-Object { $_.Value })
    $units[$unitId] = $deps
  }
}
if ($units.Count -ne 46) { throw "Expected 36 base units and 10 variants, found $($units.Count)" }
$visitState = @{}
$sortedUnits = [System.Collections.Generic.List[string]]::new()
function Visit-Unit([string]$unitId) {
  if ($visitState[$unitId] -eq 'active') { throw "Dependency cycle at $unitId" }
  if ($visitState[$unitId] -eq 'done') { return }
  $visitState[$unitId] = 'active'
  foreach ($dependency in $units[$unitId]) {
    if (-not $units.ContainsKey($dependency)) { throw "$unitId references unknown $dependency" }
    Visit-Unit $dependency
  }
  $visitState[$unitId] = 'done'
  $sortedUnits.Add($unitId)
}
foreach ($unitId in ($units.Keys | Sort-Object)) { Visit-Unit $unitId }
Write-Output 'PASS: 46 unique units (36 base + 10 variants); all dependency references exist; DAG has no cycles.'
Write-Output ('One valid topological order: ' + ($sortedUnits -join ' -> '))
Write-Output 'This verifies graph structure only, not feature completeness, acceptance or runtime.'
