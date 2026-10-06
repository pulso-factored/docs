param([string]$Document = (Join-Path $PSScriptRoot '..\TECH_SPEC_PULSO_AUTOMEJORA_V2.md'))
$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $Document).Path
$lines = Get-Content -LiteralPath $resolved
$errors = [System.Collections.Generic.List[string]]::new()
$insideFence = $false
$tableColumns = 0
$sections = [System.Collections.Generic.List[int]]::new()
for ($i = 0; $i -lt $lines.Count; $i++) {
  $line = $lines[$i]
  if ($line -match '^```') { $insideFence = -not $insideFence; $tableColumns = 0; continue }
  if ($insideFence) { continue }
  if ($line -match '^## (\d+)\.') { $sections.Add([int]$Matches[1]) }
  if ($line.StartsWith('|')) {
    $columns = [regex]::Matches($line, '(?<!\\)\|').Count - 1
    if ($tableColumns -eq 0) { $tableColumns = $columns }
    elseif ($columns -ne $tableColumns) { $errors.Add("line $($i+1): table has $columns columns; expected $tableColumns") }
  } else { $tableColumns = 0 }
  foreach ($link in [regex]::Matches($line, '\]\(([^)]+\.md)(?:#[^)]*)?\)')) {
    $target = $link.Groups[1].Value
    if ($target -notmatch '^[a-z]+://|^/') {
      $path = Join-Path (Split-Path $resolved) $target
      if (-not (Test-Path -LiteralPath $path)) { $errors.Add("line $($i+1): missing local Markdown link $target") }
    }
  }
}
if ($insideFence) { $errors.Add('Unclosed code fence') }
if (($sections -join ',') -ne ((1..30) -join ',')) { $errors.Add('Expected ordered main sections 1 through 30') }
if ($errors.Count) { $errors | Write-Output; exit 1 }
Write-Output "PASS: $($lines.Count) lines; 30 ordered sections; fences, table widths and local Markdown links checked. Semantic correctness and runtime tests are not covered."
