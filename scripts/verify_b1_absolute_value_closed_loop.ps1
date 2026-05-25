$ErrorActionPreference = "Stop"

$ROOT = "C:\Python\Mathproject_tvet_mathB"
Set-Location $ROOT

$REPORT_PATH = Join-Path $ROOT "reports\gencode_closed_loop\b1_absolute_value_verify_report.md"
$REG_PATH = Join-Path $ROOT "configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml"
$TS = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$result = [ordered]@{
    timestamp = $TS
    python_path = ""
    python_version = ""
    sys_executable = ""
    db_uri = ""
    closed_loop_exit = -1
    closed_loop_stdout = ""
    closed_loop_stderr = ""
    registry_found = $false
    registry_verified_entries = @()
    registry_abs_verified_ok = $false
    pytest_exit = -1
    pytest_stdout = ""
    pytest_stderr = ""
    generate_exit = -1
    generate_stdout = ""
    generate_stderr = ""
    sample_count = 0
    sample_problem_types = @()
    sample_checks_ok = $false
    pass = $false
    first_blocking_error = ""
}

function Test-PythonCandidate {
    param(
        [string]$ExePath,
        [string[]]$ProbeArgs
    )
    if ([string]::IsNullOrWhiteSpace($ExePath)) { return $false }
    if (-not (Test-Path $ExePath)) { return $false }
    try {
        $out = & $ExePath @ProbeArgs 2>&1
        $code = $LASTEXITCODE
        $txt = ($out | Out-String)
        if ($code -eq 0 -and $txt -notmatch "Unable to create process") { return $true }
        return $false
    } catch {
        return $false
    }
}

function Resolve-Python {
    $candidates = New-Object System.Collections.Generic.List[object]
    $cmdPy = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $cmdPy -and -not [string]::IsNullOrWhiteSpace($cmdPy.Source)) {
        $candidates.Add(@{ exe = $cmdPy.Source; probe = @("--version") })
    }
    $venvPy = Join-Path $ROOT "venv\Scripts\python.exe"
    $candidates.Add(@{ exe = $venvPy; probe = @("--version") })
    $cmdLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $cmdLauncher -and -not [string]::IsNullOrWhiteSpace($cmdLauncher.Source)) {
        $candidates.Add(@{ exe = $cmdLauncher.Source; probe = @("-3", "--version") })
        $candidates.Add(@{ exe = $cmdLauncher.Source; probe = @("--version") })
    }
    $known = @(
        "C:\Python\Mathproject_tvet_mathB\venv\Scripts\python.exe",
        "C:\Python\Mathproject\venv\Scripts\python.exe",
        "C:\Python\MathProject_AST_Research\venv\Scripts\python.exe"
    )
    foreach ($k in $known) {
        $candidates.Add(@{ exe = $k; probe = @("--version") })
    }

    foreach ($c in $candidates) {
        if (Test-PythonCandidate -ExePath $c.exe -ProbeArgs $c.probe) {
            if ($c.probe.Length -gt 0 -and $c.probe[0] -eq "-3") {
                return "$($c.exe) -3"
            }
            return $c.exe
        }
    }
    throw "python executable not found or unusable"
}

function Run-Cmd {
    param(
        [string]$FilePath,
        [string[]]$Args
    )
    $safeArgs = @()
    if ($null -ne $Args) {
        foreach ($a in $Args) {
            if ($null -ne $a -and "$a" -ne "") { $safeArgs += [string]$a }
        }
    }
    $stdout = ""
    $stderr = ""
    try {
        $all = & $FilePath @safeArgs 2>&1
        $exit = $LASTEXITCODE
        if ($null -eq $exit) { $exit = 0 }
        if ($all) { $stdout = ($all | Out-String) }
    }
    catch {
        $exit = 1
        $stderr = $_.Exception.Message
    }
    return @{
        ExitCode = $exit
        StdOut = $stdout
        StdErr = $stderr
    }
}

function Fail-If {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if ($Condition -and [string]::IsNullOrWhiteSpace($result.first_blocking_error)) {
        $result.first_blocking_error = $Message
    }
}

try {
    $resolved = Resolve-Python
    $useLauncher = $false
    $PY = $resolved
    if ($resolved -match "\s-3$") {
        $useLauncher = $true
        $PY = $resolved -replace "\s-3$",""
    }
    $result.python_path = $resolved

    $v = Run-Cmd -FilePath $PY -Args ($(if($useLauncher){@("-3","--version")}else{@("--version")}))
    $result.python_version = (($v.StdOut + $v.StdErr).Trim())
    Fail-If ($v.ExitCode -ne 0) "python --version failed"

    if ($useLauncher) { $seArgs = @("-3","-c","import sys; print(sys.executable)") } else { $seArgs = @("-c","import sys; print(sys.executable)") }
    $se = Run-Cmd -FilePath $PY -Args $seArgs
    $result.sys_executable = $se.StdOut.Trim()
    Fail-If ($se.ExitCode -ne 0) "sys.executable query failed"

    if ($useLauncher) { $dbArgs = @("-3","-c","from app import app; print(app.config.get('SQLALCHEMY_DATABASE_URI'))") } else { $dbArgs = @("-c","from app import app; print(app.config.get('SQLALCHEMY_DATABASE_URI'))") }
    $db = Run-Cmd -FilePath $PY -Args $dbArgs
    $result.db_uri = $db.StdOut.Trim()
    Fail-If ($db.ExitCode -ne 0) "DB URI query failed"

    $cl = Run-Cmd -FilePath $PY -Args ($(if($useLauncher){@("-3","scripts\run_b1_section11_gencode_closed_loop.py","--skill-id","vh_數學B1_AbsoluteValue","--max-rounds","5")}else{@("scripts\run_b1_section11_gencode_closed_loop.py","--skill-id","vh_數學B1_AbsoluteValue","--max-rounds","5")}))
    $result.closed_loop_exit = $cl.ExitCode
    $result.closed_loop_stdout = $cl.StdOut
    $result.closed_loop_stderr = $cl.StdErr
    Fail-If ($cl.ExitCode -ne 0) "closed loop command failed"

    if (Test-Path $REG_PATH) {
        $result.registry_found = $true
        $yamlRaw = Get-Content -Raw -Path $REG_PATH -Encoding UTF8
        try {
            $yamlObj = ConvertFrom-Yaml $yamlRaw
            $entries = @($yamlObj.verified_problem_types)
            $result.registry_verified_entries = $entries
        }
        catch {
            $result.registry_verified_entries = @()
            Fail-If $true "registry YAML parse failed"
        }

        foreach ($e in $result.registry_verified_entries) {
            if ($null -ne $e `
                -and $e.skill_id -eq "vh_數學B1_AbsoluteValue" `
                -and $e.problem_type_id -eq "absolute_value_numeric_evaluation" `
                -and $e.status -eq "verified" `
                -and $e.function_name -eq "generate") {
                $candPath = Join-Path $ROOT $e.candidate_path
                if (Test-Path $candPath) {
                    $result.registry_abs_verified_ok = $true
                    break
                }
            }
        }
        Fail-If (-not $result.registry_abs_verified_ok) "registry missing verified AbsoluteValue numeric entry"
    }
    else {
        Fail-If $true "registry file not found"
    }

    $pt = Run-Cmd -FilePath $PY -Args ($(if($useLauncher){@("-3","-m","pytest","tests\test_b1_absolute_value_skill_wrapper.py","-q")}else{@("-m","pytest","tests\test_b1_absolute_value_skill_wrapper.py","-q")}))
    $result.pytest_exit = $pt.ExitCode
    $result.pytest_stdout = $pt.StdOut
    $result.pytest_stderr = $pt.StdErr
    Fail-If ($pt.ExitCode -ne 0) "pytest failed"

    $genCode = "from skills.vh_數學B1_AbsoluteValue import generate; import json; qs=[generate(level=1) for _ in range(10)]; print(json.dumps(qs, ensure_ascii=False, indent=2))"
    $ge = Run-Cmd -FilePath $PY -Args ($(if($useLauncher){@("-3","-c", $genCode)}else{@("-c", $genCode)}))
    $result.generate_exit = $ge.ExitCode
    $result.generate_stdout = $ge.StdOut
    $result.generate_stderr = $ge.StdErr
    Fail-If ($ge.ExitCode -ne 0) "generate 10 questions failed"

    if ($ge.ExitCode -eq 0) {
        try {
            $samples = $ge.StdOut | ConvertFrom-Json
            $samples = @($samples)
            $result.sample_count = $samples.Count
            $ptSet = New-Object System.Collections.Generic.HashSet[string]
            $ok = $true
            foreach ($q in $samples) {
                if ([string]::IsNullOrWhiteSpace([string]$q.question_text)) { $ok = $false; break }
                if ([string]::IsNullOrWhiteSpace([string]$q.answer)) { $ok = $false; break }
                if ($q.skill_id -ne "vh_數學B1_AbsoluteValue") { $ok = $false; break }
                [void]$ptSet.Add([string]$q.problem_type_id)
            }
            $result.sample_problem_types = @($ptSet)
            if ($ptSet.Count -lt 1) { $ok = $false }

            $absVerifiedCount = @($result.registry_verified_entries | Where-Object { $_.skill_id -eq "vh_數學B1_AbsoluteValue" }).Count
            if ($absVerifiedCount -ge 2 -and $ptSet.Count -lt 2) { $ok = $false }
            $result.sample_checks_ok = $ok
            Fail-If (-not $ok) "sample validation failed"
        }
        catch {
            Fail-If $true "sample JSON parse failed"
        }
    }

    $result.pass = (
        $result.closed_loop_exit -eq 0 -and
        $result.registry_abs_verified_ok -and
        $result.pytest_exit -eq 0 -and
        $result.generate_exit -eq 0 -and
        $result.sample_checks_ok
    )
}
catch {
    Fail-If $true $_.Exception.Message
}

$reportLines = @()
$reportLines += "# B1 AbsoluteValue Closed-Loop Verify Report"
$reportLines += ""
$reportLines += "- timestamp: $($result.timestamp)"
$reportLines += "- python path: $($result.python_path)"
$reportLines += "- python version: $($result.python_version)"
$reportLines += "- sys.executable: $($result.sys_executable)"
$reportLines += "- DB URI: $($result.db_uri)"
$reportLines += ""
$reportLines += "## Closed Loop Command"
$reportLines += "- command: python scripts\run_b1_section11_gencode_closed_loop.py --skill-id vh_數學B1_AbsoluteValue --max-rounds 5"
$reportLines += "- exit code: $($result.closed_loop_exit)"
$reportLines += '```text'
$reportLines += ($result.closed_loop_stdout + $result.closed_loop_stderr).Trim()
$reportLines += '```'
$reportLines += ""
$reportLines += "## Registry Verified Entries"
$reportLines += "- registry path: $REG_PATH"
$reportLines += "- absolute_value_numeric_evaluation verified: $($result.registry_abs_verified_ok)"
$reportLines += '```json'
$reportLines += ((@{ verified_problem_types = $result.registry_verified_entries }) | ConvertTo-Json -Depth 10)
$reportLines += '```'
$reportLines += ""
$reportLines += "## Pytest"
$reportLines += "- command: python -m pytest tests\test_b1_absolute_value_skill_wrapper.py -q"
$reportLines += "- exit code: $($result.pytest_exit)"
$reportLines += '```text'
$reportLines += ($result.pytest_stdout + $result.pytest_stderr).Trim()
$reportLines += '```'
$reportLines += ""
$reportLines += "## 10-Question Samples"
$reportLines += "- command: python -c ... generate(level=1) x10"
$reportLines += "- exit code: $($result.generate_exit)"
$reportLines += "- sample count: $($result.sample_count)"
$reportLines += "- problem types: $([string]::Join(', ', $result.sample_problem_types))"
$reportLines += '```text'
$reportLines += $result.generate_stdout.Trim()
$reportLines += '```'
$reportLines += ""
$reportLines += "## Result"
$reportLines += "- PASS: $($result.pass)"
if (-not [string]::IsNullOrWhiteSpace($result.first_blocking_error)) {
    $reportLines += "- first blocking error: $($result.first_blocking_error)"
}
$reportLines += "- DB / router / practice / templates modified: false (script performs verification only)"

$reportDir = Split-Path -Parent $REPORT_PATH
if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }
Set-Content -Path $REPORT_PATH -Value ($reportLines -join "`r`n") -Encoding UTF8

if ($result.pass) {
    Write-Host "PASS - report: $REPORT_PATH"
    exit 0
}
else {
    Write-Host "FAIL - report: $REPORT_PATH"
    exit 1
}
