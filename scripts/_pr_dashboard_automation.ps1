# One-off: commit + push + open PR for dashBOARd branding, automation scripts, content-type Step 2/3.
$Title = "Dashboard (dashBOARd) branding, automation scripts, content-type Step 2/3"
$Body = @"
- Add dashBOARd sub-brand: nav label and About line only; README unchanged
- Scripts: lint-only.ps1, quick-test.ps1; rule and skill for token-aware automation
- Content type: config test for use_content_type, plan steps 2 and 3 marked done
- Docs: PLANS_TODO, PORTFOLIO markdown lint, TOKEN_AWARE_USAGE
"@
& (Join-Path $PSScriptRoot "commit-or-pr.ps1") -Action PR -Title $Title -Body $Body -RunTests
