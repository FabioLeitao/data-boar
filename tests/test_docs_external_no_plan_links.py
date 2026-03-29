"""Guardrail: external-tier Markdown must not link into planning/PMO paths.

Plans remain in the public tree under docs/plans/, but buyer-facing, legal,
and integrator docs should not offer one-click navigation into execution
detail. Allowed entry points stay in docs/README (Internal and reference),
docs/ops/, CONTRIBUTING, and plan files themselves.

See: .cursor/rules/audience-segmentation-docs.mdc
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Markdown inline links: [text](target) — strip optional title after space
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def _forbidden_plan_url(url: str) -> bool:
    raw = url.strip().split()[0].strip("<>")
    low = raw.lower()
    if ".cursor/plans" in low:
        return True
    if "/plans/" in low or low.startswith("plans/"):
        return True
    return False


def _iter_strict_markdown_files() -> list[Path]:
    """Product / external-tier docs; excludes hub, ops, plans, ADR tree."""
    allowlist_docs = {
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "README.pt_BR.md",
    }
    out: list[Path] = []
    docs_root = REPO_ROOT / "docs"
    if docs_root.is_dir():
        for path in sorted(docs_root.rglob("*.md")):
            if path in allowlist_docs:
                continue
            rel = path.relative_to(REPO_ROOT)
            parts = rel.parts
            if len(parts) >= 2 and parts[1] in ("ops", "plans"):
                continue
            if len(parts) >= 2 and parts[:2] == ("docs", "adr"):
                continue
            if len(parts) >= 2 and parts[:2] == ("docs", "private.example"):
                continue
            if len(parts) >= 2 and parts[:2] == ("docs", "private"):
                continue
            out.append(path)
    for name in (
        "README.md",
        "README.pt_BR.md",
        "SECURITY.md",
        "SECURITY.pt_BR.md",
        "CONTRIBUTING.md",
        "CONTRIBUTING.pt_BR.md",
        "AGENTS.md",
    ):
        p = REPO_ROOT / name
        if p.is_file():
            out.append(p)
    return sorted(set(out))


@pytest.mark.parametrize(
    "md_path",
    _iter_strict_markdown_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
)
def test_external_tier_markdown_has_no_plan_links(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    violations: list[str] = []
    for _m in MD_LINK_RE.finditer(text):
        target = _m.group(2)
        if _forbidden_plan_url(target):
            violations.append(target.strip().split()[0])
        assert not violations, (
            f"{md_path.relative_to(REPO_ROOT)} links into plans/ or .cursor/plans - "
            f"replace with product docs or plain text. Targets: {violations!r}"
        )


def test_forbidden_url_detector() -> None:
    assert _forbidden_plan_url("plans/PLAN_X.md")
    assert _forbidden_plan_url("../plans/PLANS_TODO.md")
    assert _forbidden_plan_url("docs/plans/foo.md")
    assert _forbidden_plan_url(".cursor/plans/foo.md")
    assert not _forbidden_plan_url("README.md")
    assert not _forbidden_plan_url("ops/COMMIT_AND_PR.md")
