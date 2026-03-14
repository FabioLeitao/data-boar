# Commit locally or create a PR (Agent Review Panel–style workflow).
# Usage:
#   .\scripts\commit-or-pr.ps1 -Action Preview
#   .\scripts\commit-or-pr.ps1 -Action Commit -Title "Short description" -Body "Bullet1`nBullet2"
#   .\scripts\commit-or-pr.ps1 -Action PR    -Title "Short description" -Body "Bullet1`nBullet2"
#   .\scripts\commit-or-pr.ps1 -Action PR    -Branch "feature/my-pr" -Title "..." -Body "..."
#   .\scripts\commit-or-pr.ps1 -Action PR    -IncludeFiles "README.md","api/routes.py" -Title "..." -Body "..."
# Run from repo root. Respects .gitignore: only non-ignored paths are staged (no audit_results.db, .env, etc.).
# Preview: show what would be committed (files + proposed message); no commit.
# -IncludeFiles: optional; only these paths are included (enables file selection). Comma-separated or array.
# PR: fetch + rebase if behind origin (keeps workflow clean), then push to origin and open PR in browser.
# PR always pushes the current branch to origin so the central repo (data-boar) reflects full progress and history.
# -RunTests: when creating a PR, run the test suite before pushing; exit without pushing if tests fail.

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Preview','Commit','PR')]
    [string]$Action,

    [string]$Title = "Update: security and docs",

    [string]$Body = "- Harden CSP and move dashboard JS to static file`n- Add rate limiting and CSP/header tests`n- Update docs and plan to-dos (EN/pt-BR, man, help)",

    [string]$Branch = "",

    [string[]]$IncludeFiles = @(),

    [switch]$RunTests = $false
)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

# Allow -IncludeFiles "path1,path2" as single string
if ($IncludeFiles.Count -eq 1 -and $IncludeFiles[0] -match ',') {
    $IncludeFiles = $IncludeFiles[0] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
}

# Changed + untracked files; only include paths not ignored by .gitignore
$changed = @()
$changed += git diff --name-only
$changed += git diff --name-only --cached
$changed += git ls-files --others --exclude-standard
$changed = $changed | Sort-Object -Unique
$toAdd = @()
foreach ($p in $changed) {
    if (-not $p) { continue }
    git check-ignore -q $p 2>$null
    if ($LASTEXITCODE -ne 0) { $toAdd += $p }
}

# Optional: restrict to selected files only (file selection)
if ($IncludeFiles.Count -gt 0) {
    $toAdd = @($toAdd | Where-Object { $f = $_; $IncludeFiles | Where-Object { $f -eq $_ -or $f -like "$_*" -or $f -replace '\\','/' -like "$($_ -replace '\\','/')*" } })
}

# Preview and Commit require something to commit
if (-not $toAdd.Count -and $Action -in 'Preview','Commit') {
    Write-Host "No files to commit (or all changes are ignored by .gitignore)."
    exit 0
}

# PR with nothing to commit: push any existing local commits and open PR (central repo gets full history).
if (-not $toAdd.Count -and $Action -eq 'PR') {
    $branchName = (git rev-parse --abbrev-ref HEAD)
    $ahead = 0
    $countOut = git rev-list --count "origin/$branchName..HEAD" 2>$null
    if ($LASTEXITCODE -eq 0 -and $countOut) { $ahead = [int]$countOut }
    else { $ahead = 1 }
    if ($ahead -gt 0) {
        if ($RunTests) {
            Write-Host "Running tests before push (-RunTests)..."
            & python -m pytest tests/ -v --tb=short -q 2>&1
            if ($LASTEXITCODE -ne 0) { Write-Host "Tests failed. Fix failures before pushing. No push performed." -ForegroundColor Red; exit 1 }
        }
        Write-Host "No new changes to commit; pushing $ahead existing local commit(s) and opening PR..."
        git fetch origin 2>$null
        $behind = git rev-list --count "HEAD..origin/$branchName" 2>$null
        if ($LASTEXITCODE -eq 0 -and $behind -and [int]$behind -gt 0) {
            Write-Host "Branch is behind origin/$branchName by $behind commit(s). Pulling with rebase..."
            git pull --rebase origin $branchName
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Rebase failed (e.g. conflicts). Resolve and run 'git rebase --continue', or 'git rebase --abort' to cancel."
                exit 1
            }
        }
        git push -u origin $branchName
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $Title = (git log -1 --format=%s)
        $Body = (git log -1 --format=%b)
        if (-not $Body) { $Body = "See commits for details." }
        $prOpened = $false
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            $bodyFile = [System.IO.Path]::GetTempFileName()
            $Body | Set-Content -Path $bodyFile -Encoding utf8
            try {
                $baseBranch = "main"
                $ref = gh repo view --json defaultBranchRef -q ".defaultBranchRef.name" 2>$null
                if ($ref) { $baseBranch = $ref }
                & gh pr create --title $Title --body-file $bodyFile --base $baseBranch --web
                if ($LASTEXITCODE -eq 0) { $prOpened = $true; Write-Host "Browser opened. Review and click 'Create pull request'." }
            } finally { Remove-Item -LiteralPath $bodyFile -ErrorAction SilentlyContinue }
        }
        if (-not $prOpened) {
            $remoteUrl = git remote get-url origin 2>$null
            if ($remoteUrl -match 'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$') {
                $defaultBranch = "main"
                if (Get-Command gh -ErrorAction SilentlyContinue) {
                    $ref = gh repo view --json defaultBranchRef -q ".defaultBranchRef.name" 2>$null
                    if ($ref) { $defaultBranch = $ref }
                } else {
                    $sym = git symbolic-ref refs/remotes/origin/HEAD 2>$null
                    if ($sym) { $defaultBranch = $sym -replace '^refs/remotes/origin/', '' }
                }
                $compareUrl = "https://github.com/$($Matches[1])/$($Matches[2].TrimEnd('.git'))/compare/$defaultBranch...$branchName"
                Write-Host "On GitHub, set base repository to $($Matches[1])/$($Matches[2].TrimEnd('.git')) and base branch to $defaultBranch (same repo = no fork)."
                Start-Process $compareUrl
            }
        }
        exit 0
    }
    Write-Host "Nothing to commit and no unpushed commits. Make changes or run with -Action Commit first."
    exit 0
}

if ($Action -eq 'Preview') {
    Write-Host "=== Preview (no commit) ===" -ForegroundColor Cyan
    Write-Host "Files that would be included (use -IncludeFiles to select only some):"
    $toAdd | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "Summary (diff --stat):"
    $untracked = $toAdd | Where-Object { -not (git ls-files --error-unmatch $_ 2>$null) }
    $untracked = @($untracked)
    if ($untracked.Count -gt 0) {
        git add -N $untracked 2>$null
        git diff --cached --stat -- $untracked
        git reset $untracked 2>$null
    }
    git diff --stat -- $toAdd
    git diff --cached --stat -- $toAdd
    Write-Host ""
    Write-Host "Proposed commit title: $Title"
    Write-Host "Proposed body (will appear in PR description):"
    $Body -split "`n" | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "To include only specific files, run with -IncludeFiles ""path1"",""path2""."
    Write-Host "Run with -Action Commit to commit locally, or -Action PR to push and open PR in browser."
    exit 0
}

# Optional: switch to or create PR branch before committing
if ($Action -eq 'PR' -and $Branch) {
    $currentBranch = (git rev-parse --abbrev-ref HEAD)
    if ($currentBranch -ne $Branch) {
        # Check if branch exists (we only use $LASTEXITCODE; discard output)
        $null = git rev-parse --verify "refs/heads/$Branch" 2>$null
        if ($LASTEXITCODE -eq 0) {
            git checkout $Branch
        } else {
            git checkout -b $Branch
        }
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "Switched from '$currentBranch' to branch '$Branch'."
    }
}

foreach ($f in $toAdd) { git add -- $f }
git status -sb

# Use separate -m for title and body so both are passed as single arguments (no word-split)
git commit -m "$Title" -m "$Body"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Committed: $Title"

if ($Action -eq 'PR') {
    $branchName = (git rev-parse --abbrev-ref HEAD)
    if ($RunTests) {
        Write-Host "Running tests before push (-RunTests)..."
        & python -m pytest tests/ -v --tb=short -q 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Host "Tests failed. Fix failures before pushing. No push performed." -ForegroundColor Red; exit 1 }
    }
    git fetch origin 2>$null
    $behind = git rev-list --count "HEAD..origin/$branchName" 2>$null
    if ($LASTEXITCODE -eq 0 -and $behind -and [int]$behind -gt 0) {
        Write-Host "Branch is behind origin/$branchName by $behind commit(s). Pulling with rebase..."
        git pull --rebase origin $branchName
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Rebase failed (e.g. conflicts). Resolve and run 'git rebase --continue', or 'git rebase --abort' to cancel."
            exit 1
        }
    }
    git push -u origin $branchName
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Pushed branch '$branchName'. Opening PR in browser (form pre-filled)..."

    $prOpened = $false
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $bodyFile = [System.IO.Path]::GetTempFileName()
        $Body | Set-Content -Path $bodyFile -Encoding utf8
        try {
            $baseBranch = "main"
            $ref = gh repo view --json defaultBranchRef -q ".defaultBranchRef.name" 2>$null
            if ($ref) { $baseBranch = $ref }
            & gh pr create --title $Title --body-file $bodyFile --base $baseBranch --web
            if ($LASTEXITCODE -eq 0) {
                $prOpened = $true
                Write-Host "Browser opened. Review the pre-filled title and description, then click 'Create pull request'."
            }
        } finally {
            Remove-Item -LiteralPath $bodyFile -ErrorAction SilentlyContinue
        }
    }

    if (-not $prOpened) {
        $remoteUrl = git remote get-url origin 2>$null
        if ($remoteUrl -match 'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$') {
            $owner = $Matches[1]
            $repo = $Matches[2].TrimEnd('.git')
            $defaultBranch = "main"
            if (Get-Command gh -ErrorAction SilentlyContinue) {
                $ref = gh repo view --json defaultBranchRef -q ".defaultBranchRef.name" 2>$null
                if ($ref) { $defaultBranch = $ref }
            } else {
                $sym = git symbolic-ref refs/remotes/origin/HEAD 2>$null
                if ($sym) { $defaultBranch = $sym -replace '^refs/remotes/origin/', '' }
            }
            $compareUrl = "https://github.com/$owner/$repo/compare/${defaultBranch}...${branchName}"
            Write-Host "Opening compare page in browser (create PR there): $compareUrl"
            Write-Host "On GitHub, set base repository to $owner/$repo and base branch to $defaultBranch (same repo = no fork)."
            Start-Process $compareUrl
        } else {
            Write-Host "Push succeeded. Open GitHub, go to your repo, and create a PR from branch '$branchName'."
        }
    }
}
