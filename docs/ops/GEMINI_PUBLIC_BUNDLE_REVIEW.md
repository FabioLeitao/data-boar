# External LLM review bundle (Gemini) — safe workflow

**Portuguese (pt-BR):** [GEMINI_PUBLIC_BUNDLE_REVIEW.pt_BR.md](GEMINI_PUBLIC_BUNDLE_REVIEW.pt_BR.md)

**After a `cat` incident:** step-by-step recovery and the Windows meta script **`scripts/recovery-doc-bundle-sanity.ps1`** — **[DOC_BUNDLE_RECOVERY_PLAYBOOK.md](DOC_BUNDLE_RECOVERY_PLAYBOOK.md)** ([pt-BR](DOC_BUNDLE_RECOVERY_PLAYBOOK.pt_BR.md)).

## Authority (Gemini vs Git + tests)

External LLM review (e.g. Gemini on **`export_public_gemini_bundle.py`** output) is **optional batch triage**—not a stand-alone audit report and **not** a substitute for **`git` history**, **CI**, or **pytest**. Use it like other **external digests** (e.g. Wabbix / WRB-style inputs): good for **prioritization**, still subordinate to reproducible checks. In-repo guardrails include **`--verify`** on bundle export, **`audit_concat_*`** helpers where you use them, **`recovery-doc-bundle-sanity.ps1`**, and the **recovery playbook** when a bundle goes wrong.

**After each run:** capture suggestions in **[plans/PLAN_GEMINI_FEEDBACK_TRIAGE.md](../plans/PLAN_GEMINI_FEEDBACK_TRIAGE.md)** (optional to-dos, non-authoritative) before promoting anything into **[PLANS_TODO.md](../plans/PLANS_TODO.md)** or an issue.

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

| Flag                | Meaning                                                   |
| ----                | -------                                                   |
| `--compliance-yaml` | Also include `docs/compliance-samples/*.yaml`             |
| `--cursor`          | Include `.cursor/**/*.md` (large; usually off)            |
| `--plans`           | Include `docs/plans/**/*.md` (large; usually off)         |
| `--no-workflows`    | Skip `.github/workflows/*` and `dependabot.yml`           |
| `--verify`          | After writing, re-read each section and diff against disk |
| `--dry-run`         | Show how many paths would be included                     |

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
- **Sliding-window “puzzle piece” heuristic:** `scripts/audit_concat_sliding_window.py` builds an index of every *N*-line window over tracked `*.md` / `*.yaml` / `*.yml`, then marks which lines in your concatenated blob are covered by at least one matching window. **Uncovered** runs may be glue between files, manual edits, or text that no longer exists on disk — **not proof** of loss (generic lines and boundary effects happen). Example:

  ```bash
  uv run python scripts/audit_concat_sliding_window.py \
    -i docs/private/mess_concatenated_gemini_sanity_check/sobre-data-boar.md \
    --window 25 --strip-bundle-markers --show-sample-matches 15
  ```

  Optional: `--rstrip-lines` if editors varied trailing spaces; `--include-private-corpus` only if you intentionally want `docs/private/**` in the corpus. `--fail-if-uncovered-pct-above 0` exits non-zero when any line stays uncovered (strict CI-style gate; often too noisy for real blobs).
  **Multi-pass:** `--sweep-windows 12,15,18,22,25,30` prints one comparison table (run again with `--rstrip-lines` to compare whitespace barriers). See **[DOC_BUNDLE_RECOVERY_PLAYBOOK.md](DOC_BUNDLE_RECOVERY_PLAYBOOK.md)** § Multi-pass.

- **Operator notification policy:** [OPERATOR_NOTIFICATION_CHANNELS.md](OPERATOR_NOTIFICATION_CHANNELS.md).
