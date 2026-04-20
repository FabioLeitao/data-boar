"""
Load a structured questionnaire pack from YAML (exported from private DOCX or authored by hand).

Public repo ships schema + generic samples only — no proprietary wording from operator DOCX.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class MaturityQuestion:
    id: str
    prompt: str


@dataclass(frozen=True)
class MaturitySection:
    id: str
    title: str
    questions: tuple[MaturityQuestion, ...]


@dataclass(frozen=True)
class MaturityPack:
    version: int
    sections: tuple[MaturitySection, ...]


def load_maturity_pack(path: str | Path) -> MaturityPack:
    """Parse YAML into a pack. Raises FileNotFoundError, ValueError, or yaml.YAMLError."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    raw = p.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("pack root must be a mapping")
    version = int(data.get("version", 1))
    sections_raw = data.get("sections")
    if not isinstance(sections_raw, list):
        raise ValueError("sections must be a list")
    sections: list[MaturitySection] = []
    for s in sections_raw:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("id") or "").strip()
        title = str(s.get("title") or "").strip()
        qs: list[MaturityQuestion] = []
        for q in s.get("questions") or []:
            if not isinstance(q, dict):
                continue
            qid = str(q.get("id") or "").strip()
            prompt = str(q.get("prompt") or "").strip()
            if qid and prompt:
                qs.append(MaturityQuestion(id=qid, prompt=prompt))
        if sid and title and qs:
            sections.append(MaturitySection(id=sid, title=title, questions=tuple(qs)))
    if not sections:
        raise ValueError("pack has no valid sections with questions")
    return MaturityPack(version=version, sections=tuple(sections))
