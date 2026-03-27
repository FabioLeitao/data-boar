# External LLM review bundle (Gemini) — safe workflow

**Portuguese (pt-BR):** [GEMINI_PUBLIC_BUNDLE_REVIEW.pt_BR.md](GEMINI_PUBLIC_BUNDLE_REVIEW.pt_BR.md)

This runbook avoids **manual `cat *.md`** mistakes: the bundle is built from **`git ls-files` only**, excludes **`docs/private/`**, and wraps every file as:

```text
--- FILE: path/relative/to/repo ---
<exact file contents>
```

## Build (recommended)

From the repo root:

```bash
uv run python scripts/export_public_gemini_bundle.py \
  --output docs/private/gemini_bundles/public_bundle_$(date -I).txt \
  --compliance-yaml \
  --verify
```

On Linux/macOS you can use:

```bash
./scripts/export_public_gemini_bundle.sh -o /tmp/public_bundle.txt --compliance-yaml --verify
```

Flags:

| Flag | Meaning |
| ---- | ------- |
| `--compliance-yaml` | Also include `docs/compliance-samples/*.yaml` |
| `--cursor` | Include `.cursor/**/*.md` (large; usually off) |
| `--plans` | Include `docs/plans/**/*.md` (large; usually off) |
| `--no-workflows` | Skip `.github/workflows/*` and `dependabot.yml` |
| `--verify` | After writing, re-read each section and diff against disk |
| `--dry-run` | Show how many paths would be included |

**Output path:** keep bundles under **`docs/private/...`** (gitignored) so nothing accidental lands in Git.

## Suggested Gemini prompt (copy/paste)

Use the bundle as **the only** large attachment; do **not** add private notes.

```text
You are reviewing public technical documentation and CI YAML for an open-source product (Data Boar — LGPD-style data auditing / sensitivity detection).

Input: a single text with sections starting with lines exactly:
--- FILE: <path> ---
followed by the file body. Do not assume private or unpublished files exist.

Tasks:
1) P0/P1/P2 issues (same semantics as our internal checklist): onboarding, security posture, contradiction, missing limits, CI footguns.
2) If YAML samples: operational footguns and maintainability (not legal opinions).
3) Do not invent features; if unsure, say “confirm in code”.

Output format:
## Executive summary (5 bullets max)
## P0
## P1
## P2
## Questions the docs leave open
```

Tighten or shorten the prompt when the bundle is near the model’s context limit (`--dry-run` helps gauge size).

## Related automation

- **Headerless legacy bundles:** `scripts/audit_concatenated_markdown.py` (H1 heuristic or `--cat-order` byte split).
- **Operator notification policy:** [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md).
