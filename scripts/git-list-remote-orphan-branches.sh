#!/usr/bin/env bash
# git-list-remote-orphan-branches.sh
# Read-only inventory of remote branches that have *no* open PR backing them.
#
# Why this exists (Slack 2026-04-28, message ts 1777370978.136399):
#   The Cloud-Agent fleet leaves dozens of `cursor/sre-*` remote branches behind.
#   Most of them back live OPEN PRs --- those are *not* orphans, deleting them
#   would auto-close the PR and lose the audit paper trail (see
#   `docs/ops/sre_audits/FABRICATED_CLAIMS_INDEX.md`, mass-close fabrication).
#
#   This script answers exactly one question: "which remote branches have NO
#   open PR right now?" It never deletes anything. It prints
#   `git push origin --delete <branch>` lines you can copy after a final
#   read --- per `docs/ops/BRANCH_AND_DOCKER_CLEANUP.md` rules.
#
# Doctrine:
#   * `docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md` Section 1.3 ---
#     no surprise side effects: read-only by design.
#   * `docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md` Section 3 ---
#     diagnostic on fall: emit the list with provenance, not silent action.
#   * `AGENTS.md` *Risk posture* --- destructive ops require operator review.
#
# Usage (repo root):
#   ./scripts/git-list-remote-orphan-branches.sh
#   ./scripts/git-list-remote-orphan-branches.sh --pattern 'cursor/sre-*'
#   ./scripts/git-list-remote-orphan-branches.sh --include-stale-days 14
#
# Requires: git, gh (authenticated for the data-boar repo).

set -euo pipefail

PATTERN=""
STALE_DAYS=""
KEEP_REGEX='^(main|HEAD|auditoria-ia|chore/.*release.*|chore/.*beta.*)$'

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pattern)
            PATTERN="$2"; shift 2;;
        --include-stale-days)
            STALE_DAYS="$2"; shift 2;;
        -h|--help)
            sed -n '1,40p' "$0"; exit 0;;
        *)
            echo "Unknown arg: $1" >&2; exit 2;;
    esac
done

command -v git >/dev/null || { echo "git not found" >&2; exit 1; }
command -v gh  >/dev/null || { echo "gh not found (install GitHub CLI and 'gh auth login')" >&2; exit 1; }

echo "==> Refreshing remote refs (git fetch --prune origin)" >&2
git fetch --prune origin >/dev/null

tmp_pr=$(mktemp)
tmp_branches=$(mktemp)
trap 'rm -f "$tmp_pr" "$tmp_branches"' EXIT

# Open-PR head refs (single source of truth --- a branch with an open PR is NEVER orphan)
gh pr list --state open --limit 500 --json headRefName -q '.[].headRefName' \
    | sort -u > "$tmp_pr"

# Remote branches (strip the leading 'origin/', drop the HEAD pointer line and
# any spurious entry that does not look like a real branch path).
git for-each-ref --format='%(refname:short)' refs/remotes/origin \
    | sed 's|^origin/||' \
    | grep -v '^HEAD$' \
    | grep -v '^$' \
    | grep -v '^origin$' \
    | sort -u > "$tmp_branches"

total_remote=$(wc -l < "$tmp_branches")
total_open_prs=$(wc -l < "$tmp_pr")

if [[ -n "$PATTERN" ]]; then
    pattern_filter() { grep -E "$PATTERN" || true; }
else
    pattern_filter() { cat; }
fi

# Orphans = remote branches not in the open-PR set, minus the explicit keep list.
orphans=$(comm -23 "$tmp_branches" "$tmp_pr" | grep -Ev "$KEEP_REGEX" | pattern_filter || true)

echo
echo "Remote branch inventory (origin):"
echo "  total remote refs    : $total_remote"
echo "  branches with open PR: $total_open_prs"
if [[ -n "$PATTERN" ]]; then
    echo "  --pattern filter     : $PATTERN"
fi
echo

if [[ -z "$orphans" ]]; then
    echo "No orphan branches found (every non-protected remote branch is backed by an open PR)."
    exit 0
fi

echo "Orphan branches (no open PR, not in keep-list):"
while IFS= read -r b; do
    [[ -z "$b" ]] && continue
    last_commit=$(git log -1 --format='%ci' "origin/$b" 2>/dev/null || echo 'unknown')
    ahead=$(git rev-list --count "origin/main..origin/$b" 2>/dev/null || echo '?')
    behind=$(git rev-list --count "origin/$b..origin/main" 2>/dev/null || echo '?')
    if [[ -n "$STALE_DAYS" && "$last_commit" != 'unknown' ]]; then
        # Optional age filter: skip rows newer than STALE_DAYS.
        last_epoch=$(date -d "$last_commit" +%s 2>/dev/null || echo 0)
        cutoff=$(date -d "$STALE_DAYS days ago" +%s 2>/dev/null || echo 0)
        if [[ "$last_epoch" -gt "$cutoff" ]]; then
            continue
        fi
    fi
    printf '  - %-60s  last=%s  ahead=%s  behind=%s\n' \
        "$b" "$last_commit" "$ahead" "$behind"
done <<< "$orphans"

echo
echo "Suggested commands (copy + paste only after reviewing each branch):"
while IFS= read -r b; do
    [[ -z "$b" ]] && continue
    printf '  git push origin --delete %s\n' "$b"
done <<< "$orphans"

echo
echo "This script is read-only. It does NOT delete anything."
echo "Doctrine: DEFENSIVE_SCANNING_MANIFESTO Section 1.3, THE_ART_OF_THE_FALLBACK Section 3, AGENTS.md Risk posture."
