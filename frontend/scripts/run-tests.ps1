param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$testFiles = @(
  "src/__tests__/page-interactions.test.js",
  "src/__tests__/api-mock.test.js",
  "src/__tests__/coverage-boost.test.js"
)

$coverageRequested = $false
if ($ExtraArgs) {
  $coverageRequested = $ExtraArgs -contains "--coverage"
}

if (-not $coverageRequested) {
  & node --test --experimental-test-isolation=none @testFiles
  exit $LASTEXITCODE
}

$coverageDir = Join-Path $projectRoot "coverage"
$v8Dir = Join-Path $coverageDir ("v8-" + [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
$reportFile = Join-Path $coverageDir "term-report.txt"

New-Item -ItemType Directory -Force -Path $coverageDir | Out-Null
New-Item -ItemType Directory -Force -Path $v8Dir | Out-Null

$env:NODE_V8_COVERAGE = $v8Dir
$output = & node --test --experimental-test-isolation=none --experimental-test-coverage @testFiles 2>&1
$exitCode = $LASTEXITCODE
Remove-Item Env:NODE_V8_COVERAGE -ErrorAction SilentlyContinue

$output | Set-Content -Path $reportFile -Encoding UTF8
$output

if ($exitCode -ne 0) {
  exit $exitCode
}

& node scripts/write-lcov.js $v8Dir
exit $LASTEXITCODE
