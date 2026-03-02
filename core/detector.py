"""
Unified sensitivity detector: regex (from config or built-in) + ML (terms from external config).
Returns (sensitivity, pattern_detected, norm_tag, confidence); no storage of sample content.

To reduce false positives on song lyrics and music tablature/chord sheets:
- Content heuristics detect lyrics (verse/chorus keywords, short lines) and tabs (digit/pipe lines).
- In that context, weak patterns (DATE_DMY, PHONE_BR) are downgraded to MEDIUM; ML confidence
  is penalized so borderline cases stay MEDIUM/LOW. Strong PII (CPF, EMAIL, CREDIT_CARD, SSN)
  still reports HIGH.
"""
from pathlib import Path
from typing import Any

import re

# Optional ML deps (numpy/pandas/sklearn) - fail gracefully if not installed
try:
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    pd = None
    TfidfVectorizer = None
    RandomForestClassifier = None

# Built-in regex patterns (LGPD/GDPR/CCPA/HIPAA/GLBA relevant)
DEFAULT_PATTERNS = {
    "LGPD_CPF": (r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "LGPD Art. 5"),
    "LGPD_CNPJ": (r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", "LGPD Art. 5"),
    "EMAIL": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "GDPR Art. 4(1)"),
    "CREDIT_CARD": (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "PCI/GLBA"),
    "PHONE_BR": (r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b", "LGPD Art. 5"),
    "CCPA_SSN": (r"\b\d{3}-\d{2}-\d{4}\b", "CCPA"),
    "DATE_DMY": (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "Personal data context"),
}

# Default ML training terms (sensitive=1, non_sensitive=0)
DEFAULT_ML_TERMS = [
    ("cpf", 1), ("email", 1), ("credit card", 1), ("password", 1), ("senha", 1),
    ("health record", 1), ("saude", 1), ("data de nascimento", 1), ("birth date", 1),
    ("ethnic origin", 1), ("political opinion", 1), ("religion", 1), ("gender", 1),
    ("nome completo", 1), ("rg", 1), ("ssn", 1), ("salary", 1), ("salário", 1),
    ("system_log", 0), ("item_count", 0), ("config_file", 0), ("temp_data", 0),
    ("id_interno", 0), ("quantidade_estoque", 0),
    # Lyrics and music notation context → reduce false positives
    ("lyrics", 0), ("verse", 0), ("chorus", 0), ("bridge", 0), ("refrão", 0), ("estrofe", 0),
    ("letra", 0), ("cifra", 0), ("tab", 0), ("tablature", 0), ("chord", 0), ("guitar", 0),
    ("intro", 0), ("outro", 0), ("riff", 0), ("bass", 0), ("capo", 0), ("tuning", 0),
]

# Regex patterns that often match in lyrics/tabs without real PII (dates in lyrics, digits in tabs)
WEAK_PATTERNS_IN_ENTERTAINMENT = frozenset({"DATE_DMY", "PHONE_BR"})


def _looks_like_lyrics(sample: str) -> bool:
    """
    Heuristic: content resembles song lyrics (short lines, verse/chorus keywords).
    Used to downgrade false positives from dates/numbers in lyrics.
    """
    if not sample or len(sample.strip()) < 30:
        return False
    lower = sample.lower()
    keywords = (
        "verse", "chorus", "bridge", "refrão", "estrofe", "letra", "lyrics",
        "intro", "outro", "la la", "na na", "oh oh", "yeah yeah", "repeat",
    )
    if any(k in lower for k in keywords):
        return True
    lines = [ln.strip() for ln in sample.splitlines() if ln.strip()]
    if len(lines) >= 5:
        avg_len = sum(len(ln) for ln in lines) / len(lines)
        if avg_len < 55:
            return True
    return False


def _looks_like_music_tab(sample: str) -> bool:
    """
    Heuristic: content resembles guitar/bass tablature or chord sheets.
    Used to downgrade false positives from digit sequences (tabs) or chord names.
    """
    if not sample or len(sample.strip()) < 20:
        return False
    lines = [ln.strip() for ln in sample.splitlines() if ln.strip()]
    tab_score = 0
    chord_score = 0
    for ln in lines[:30]:
        if len(ln) > 2:
            # Tab: digits, |, -, [, ], h, p, b, /, \
            tab_chars = sum(1 for c in ln if c in "0123456789|-[ ]hp/b\\")
            if tab_chars >= min(4, len(ln) // 2):
                tab_score += 1
            # Chord line: capital letter + optional m/7/dim etc.
            if re.match(r"^[\sA-G][mM0-9#b\s/dim]*$", ln) and len(ln) >= 2:
                chord_score += 1
    if tab_score >= 2 or chord_score >= 2:
        return True
    lower = sample.lower()
    if any(k in lower for k in ("tab", "tablature", "cifra", "chord", "capo", "tuning", "e|---", "a|---", "b|---")):
        return True
    return False


def _load_regex_overrides(path: str | None) -> dict[str, tuple[str, str]]:
    """Load name -> (pattern, norm_tag) from YAML/JSON file."""
    if not path or not Path(path).exists():
        return {}
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yaml", ".yml"):
        import yaml
        data = yaml.safe_load(raw)
    else:
        import json
        data = json.loads(raw)
    if not isinstance(data, (list, dict)):
        return {}
    out = {}
    items = data if isinstance(data, list) else data.get("patterns", data.get("regex", []))
    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "")
            pattern = item.get("pattern", "")
            norm = item.get("norm_tag", "Custom")
            if name and pattern:
                out[name] = (pattern, norm)
    return out


def _load_ml_patterns(path: str | None) -> list[tuple[str, int]]:
    """Load (text, label) from YAML/JSON; label 1=sensitive, 0=non_sensitive."""
    if not path or not Path(path).exists():
        return []
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() in (".yaml", ".yml"):
        import yaml
        data = yaml.safe_load(raw)
    else:
        import json
        data = json.loads(raw)
    if not isinstance(data, (list, dict)):
        return []
    items = data if isinstance(data, list) else data.get("patterns", data.get("terms", []))
    out = []
    for item in items:
        if isinstance(item, dict):
            text = item.get("text", "").strip()
            label = 1 if item.get("label", "sensitive") in ("sensitive", 1, "1") else 0
            if text:
                out.append((text.lower(), label))
    return out


class SensitivityDetector:
    """
    Hybrid detector: regex first, then ML on column name + sample context.
    analyze(column_name, sample_text) -> (sensitivity_level, pattern_detected, norm_tag, confidence).
    """

    def __init__(
        self,
        regex_overrides_path: str | None = None,
        ml_patterns_path: str | None = None,
    ):
        self.patterns = dict(DEFAULT_PATTERNS)
        over = _load_regex_overrides(regex_overrides_path)
        for k, v in over.items():
            self.patterns[k] = v
        self._compiled = {name: re.compile(pat) for name, (pat, _) in self.patterns.items()}

        self._ml_available = False
        self._vectorizer = None
        self._model = None
        if _ML_AVAILABLE:
            terms = _load_ml_patterns(ml_patterns_path) or DEFAULT_ML_TERMS
            if terms:
                texts = [t[0] for t in terms]
                labels = [t[1] for t in terms]
                self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
                X = self._vectorizer.fit_transform(texts)
                self._model = RandomForestClassifier(n_estimators=100)
                self._model.fit(X, labels)
                self._ml_available = True

    def analyze(self, column_name: str, sample_text: str) -> tuple[str, str, str, int]:
        """
        Returns (sensitivity_level, pattern_detected, norm_tag, ml_confidence 0-100).
        Does not store sample_text. Downgrades classification when content looks like
        song lyrics or music tabs to reduce false positives.
        """
        combined = f"{column_name} {sample_text}"
        sample_only = sample_text or ""
        entertainment_context = _looks_like_lyrics(sample_only) or _looks_like_music_tab(sample_only)

        found_patterns: list[tuple[str, str]] = []
        for name, (_, norm_tag) in self.patterns.items():
            rex = self._compiled.get(name)
            if rex and rex.search(combined):
                found_patterns.append((name, norm_tag))

        ml_confidence = 0
        if self._ml_available and self._model and self._vectorizer:
            try:
                X = self._vectorizer.transform([combined.lower()])
                prob = self._model.predict_proba(X)[0][1]
                ml_confidence = int(round(prob * 100))
            except Exception:
                pass

        if entertainment_context:
            ml_confidence = max(0, ml_confidence - 25)
            if found_patterns:
                matched_names = {p[0] for p in found_patterns}
                only_weak = matched_names <= WEAK_PATTERNS_IN_ENTERTAINMENT
                if only_weak:
                    names = ", ".join(p[0] for p in found_patterns)
                    norms = ", ".join(p[1] for p in found_patterns)
                    return "MEDIUM", names + " (lyrics/tabs context)", norms, min(ml_confidence, 55)
                names = ", ".join(p[0] for p in found_patterns)
                norms = ", ".join(p[1] for p in found_patterns)
                return "HIGH", names, norms, max(ml_confidence, 70)
        else:
            if found_patterns:
                names = ", ".join(p[0] for p in found_patterns)
                norms = ", ".join(p[1] for p in found_patterns)
                return "HIGH", names, norms, max(ml_confidence, 80)
        if ml_confidence >= 70:
            return "HIGH", "ML_DETECTED", "LGPD/GDPR/CCPA context", ml_confidence
        if ml_confidence >= 40:
            return "MEDIUM", "ML_POTENTIAL", "Potential personal data", ml_confidence
        return "LOW", "GENERAL", "Non-personal", ml_confidence
