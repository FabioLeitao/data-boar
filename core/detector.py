"""
Unified sensitivity detector: regex (from config or built-in) + ML (TF-IDF + RandomForest)
+ optional DL (sentence embeddings + classifier). Returns (sensitivity, pattern_detected, norm_tag, confidence);
no storage of sample content.

Pipeline:
1. Regex: built-in + optional overrides from config.
2. ML: training terms from ml_patterns_file or sensitivity_detection.ml_terms (inline).
3. DL (hybrid): when available, training terms from dl_patterns_file or sensitivity_detection.dl_terms;
   confidence is combined with ML (e.g. max(ml_confidence, dl_confidence)).

To reduce false positives on song lyrics and music tablature/chord sheets:
- Content heuristics detect lyrics (verse/chorus keywords, short lines) and tabs (digit/pipe lines).
- In that context, weak patterns (DATE_DMY, PHONE_BR) are downgraded to MEDIUM; ML/DL confidence
  is penalized so borderline cases stay MEDIUM/LOW. Strong PII (CPF, EMAIL, CREDIT_CARD, SSN)
  still reports HIGH.
"""
from pathlib import Path
from typing import Any

import re

from core.dl_backend import DLClassifier, is_available as dl_available

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

# Default ML training terms (sensitive=1, non_sensitive=0).
# Includes LGPD/GDPR-relevant PII plus a subset of sensitive categories (health, religion, political,
# gender, biometric, genetic, race, union, PEP, sex life) for out-of-the-box detection.
# See docs/PLAN_SENSITIVE_CATEGORIES_ML_DL.md and docs/sensitivity_terms_sensitive_categories.example.yaml
# for the full list; override via ml_patterns_file or sensitivity_detection.ml_terms to customize.
DEFAULT_ML_TERMS = [
    ("cpf", 1), ("email", 1), ("credit card", 1), ("password", 1), ("senha", 1),
    ("health record", 1), ("saude", 1), ("data de nascimento", 1), ("birth date", 1),
    ("ethnic origin", 1), ("political opinion", 1), ("religion", 1), ("gender", 1),
    ("nome completo", 1), ("rg", 1), ("ssn", 1), ("salary", 1), ("salário", 1),
    # Sensitive categories (LGPD Art. 5 II, 11; GDPR Art. 9) – additive subset for out-of-the-box
    ("religious affiliation", 1), ("religiao", 1), ("political affiliation", 1), ("filiacao politica", 1),
    ("biometric data", 1), ("genetic data", 1), ("union affiliation", 1), ("sindicato", 1),
    ("politically exposed person", 1), ("PEP", 1), ("race", 1), ("skin color", 1), ("sexual orientation", 1),
    ("disability", 1), ("deficiencia", 1), ("condicao de saude", 1), ("health condition", 1),
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


def _ml_terms_from_inline_or_file(
    inline: list[dict[str, Any]] | list[tuple[str, int]] | None,
    path: str | None,
) -> list[tuple[str, int]]:
    """ML training terms: prefer inline when non-empty; else file; else DEFAULT_ML_TERMS."""
    if inline:
        out = []
        for t in inline:
            if isinstance(t, dict):
                text = (t.get("text") or "").strip().lower()
                label = 1 if t.get("label", "sensitive") in ("sensitive", 1, "1") else 0
                if text:
                    out.append((text, label))
            elif isinstance(t, (list, tuple)) and len(t) >= 2:
                text = str(t[0]).strip().lower()
                label = 1 if t[1] in (1, "1", "sensitive") else 0
                if text:
                    out.append((text, label))
        if out:
            return out
    return _load_ml_patterns(path) or DEFAULT_ML_TERMS


def _load_dl_terms(
    path: str | None,
    inline: list[dict[str, Any]] | list[tuple[str, int]] | None,
) -> list[tuple[str, int]]:
    """DL training terms: prefer inline (list of {text, label}); else load from path (same format as ML)."""
    if inline:
        out = []
        for t in inline:
            if isinstance(t, dict):
                text = (t.get("text") or "").strip().lower()
                label = 1 if t.get("label", "sensitive") in ("sensitive", 1, "1") else 0
                if text:
                    out.append((text, label))
            elif isinstance(t, (list, tuple)) and len(t) >= 2:
                text = str(t[0]).strip().lower()
                label = 1 if t[1] in (1, "1", "sensitive") else 0
                if text:
                    out.append((text, label))
        if out:
            return out
    return _load_ml_patterns(path)


def _detect_possible_minor(column_name: str, sample_text: str, minor_age_threshold: int) -> bool:
    """
    Heuristic detection of possible minor data based on column name (including PT-BR variants/acronyms)
    and sample values (dates of birth or numeric ages).
    """
    col = (column_name or "").lower()
    sample = sample_text or ""

    # DOB-like column name tokens (EN + PT-BR, including acronyms)
    dob_tokens = (
        "date of birth",
        "birth date",
        "birthdate",
        "data de nascimento",
        "data nascimento",
        "data de nasc",
        "nascimento",
        "dob",
        "ddn",
        "dn",
        "nasc",
        "dtn",
    )
    # Age-like column name tokens (EN + PT-BR, including acronyms)
    age_tokens = (
        "age",
        "person age",
        "idade",
        "idade_atual",
        "idade_pessoa",
        "faixa etaria",
        "faixa etária",
        "idd",
    )

    is_dob_like = any(tok in col for tok in dob_tokens)
    is_age_like = any(tok in col for tok in age_tokens)
    if not is_dob_like and not is_age_like:
        return False

    from datetime import date

    # Helper: compute age from year, month, day (rough, but enough for < threshold vs >= threshold)
    def _age_from_ymd(y: int, m: int, d: int) -> int | None:
        try:
            today = date.today()
            dob = date(y, m, d)
            years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return years
        except Exception:
            return None

    # If age-like and we see numeric ages, use them directly
    if is_age_like:
        for match in re.findall(r"\b\d{1,3}\b", sample):
            try:
                val = int(match)
            except ValueError:
                continue
            if 0 <= val < minor_age_threshold:
                return True

    # If DOB-like, try parsing common date formats in the sample text
    if is_dob_like:
        # DMY (e.g. 15/03/2010 or 1/5/12)
        for m in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", sample):
            d_s, m_s, y_s = m
            try:
                d_i = int(d_s)
                m_i = int(m_s)
                y_i = int(y_s)
            except ValueError:
                continue
            if y_i < 100:
                # Simple century heuristic: 00–30 => 2000–2030, else 1900–1999
                y_i = 2000 + y_i if y_i <= 30 else 1900 + y_i
            years = _age_from_ymd(y_i, m_i, d_i)
            if years is not None and 0 <= years < minor_age_threshold:
                return True

        # YMD (e.g. 2010-03-15 or 2010/03/15)
        for m in re.findall(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", sample):
            y_s, m_s, d_s = m
            try:
                y_i = int(y_s)
                m_i = int(m_s)
                d_i = int(d_s)
            except ValueError:
                continue
            years = _age_from_ymd(y_i, m_i, d_i)
            if years is not None and 0 <= years < minor_age_threshold:
                return True

        # MDY (e.g. 03-15-2010)
        for m in re.findall(r"\b(\d{1,2})[-](\d{1,2})[-](\d{4})\b", sample):
            m_s, d_s, y_s = m
            try:
                m_i = int(m_s)
                d_i = int(d_s)
                y_i = int(y_s)
            except ValueError:
                continue
            years = _age_from_ymd(y_i, m_i, d_i)
            if years is not None and 0 <= years < minor_age_threshold:
                return True

    return False


class SensitivityDetector:
    """
    Hybrid detector: regex first, then ML (TF-IDF + RandomForest), then optional DL (sentence embeddings + classifier).
    analyze(column_name, sample_text) -> (sensitivity_level, pattern_detected, norm_tag, confidence).
    ML/DL training terms can come from config files (ml_patterns_file, dl_patterns_file) or inline (sensitivity_detection.ml_terms / dl_terms).
    """

    def __init__(
        self,
        regex_overrides_path: str | None = None,
        ml_patterns_path: str | None = None,
        ml_terms_inline: list[dict[str, Any]] | list[tuple[str, int]] | None = None,
        dl_patterns_path: str | None = None,
        dl_terms_inline: list[dict[str, Any]] | list[tuple[str, int]] | None = None,
        detection_config: dict[str, Any] | None = None,
    ):
        self.patterns = dict(DEFAULT_PATTERNS)
        over = _load_regex_overrides(regex_overrides_path)
        for k, v in over.items():
            self.patterns[k] = v
        self._compiled = {name: re.compile(pat) for name, (pat, _) in self.patterns.items()}

        # ML terms: inline overrides file; file overrides default
        ml_terms = _ml_terms_from_inline_or_file(ml_terms_inline, ml_patterns_path)
        self._ml_available = False
        self._vectorizer = None
        self._model = None
        if _ML_AVAILABLE and ml_terms:
            texts = [t[0] for t in ml_terms]
            labels = [t[1] for t in ml_terms]
            self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            X = self._vectorizer.fit_transform(texts)
            self._model = RandomForestClassifier(n_estimators=100)
            self._model.fit(X, labels)
            self._ml_available = True

        # DL terms: inline or from dl_patterns_path (same file format as ML)
        dl_terms = _load_dl_terms(dl_patterns_path, dl_terms_inline)
        self._dl_classifier: DLClassifier | None = None
        if dl_terms and dl_available():
            self._dl_classifier = DLClassifier(dl_terms)
            if not self._dl_classifier.is_ready:
                self._dl_classifier = None

        # Minor detection: threshold from config (default 18); other options (e.g. full_scan, cross_reference) are used by connectors/report
        det = detection_config or {}
        try:
            self._minor_age_threshold = int(det.get("minor_age_threshold", 18))
        except (TypeError, ValueError):
            self._minor_age_threshold = 18

    def analyze(self, column_name: str, sample_text: str) -> tuple[str, str, str, int]:
        """
        Returns (sensitivity_level, pattern_detected, norm_tag, ml_confidence 0-100).
        Does not store sample_text. Downgrades classification when content looks like
        song lyrics or music tabs to reduce false positives.
        """
        combined = f"{column_name} {sample_text}"
        sample_only = sample_text or ""
        entertainment_context = _looks_like_lyrics(sample_only) or _looks_like_music_tab(sample_only)

        # Heuristic: possible minor data based on DOB/age (EN + PT-BR)
        possible_minor = _detect_possible_minor(column_name, sample_only, self._minor_age_threshold)

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

        # Hybrid DL step: when available, combine with ML (take max to avoid missing semantic matches)
        dl_confidence = 0
        if self._dl_classifier and self._dl_classifier.is_ready:
            prob = self._dl_classifier.predict_proba(combined)
            if prob is not None:
                dl_confidence = int(round(prob * 100))
        combined_confidence = max(ml_confidence, dl_confidence)

        if entertainment_context:
            combined_confidence = max(0, combined_confidence - 25)
            if found_patterns:
                matched_names = {p[0] for p in found_patterns}
                only_weak = matched_names <= WEAK_PATTERNS_IN_ENTERTAINMENT
                if only_weak and not possible_minor:
                    names = ", ".join(p[0] for p in found_patterns)
                    norms = ", ".join(p[1] for p in found_patterns)
                    return "MEDIUM", names + " (lyrics/tabs context)", norms, min(combined_confidence, 55)
                names = ", ".join(p[0] for p in found_patterns)
                norms = ", ".join(p[1] for p in found_patterns)
                if possible_minor:
                    names = f"DOB_POSSIBLE_MINOR, {names}"
                    norms = "LGPD Art. 14 – possible minor data; GDPR Art. 8" + (", " + norms if norms else "")
                return "HIGH", names, norms, max(combined_confidence, 70)
        else:
            if found_patterns:
                names = ", ".join(p[0] for p in found_patterns)
                norms = ", ".join(p[1] for p in found_patterns)
                if possible_minor:
                    names = f"DOB_POSSIBLE_MINOR, {names}"
                    norms = "LGPD Art. 14 – possible minor data; GDPR Art. 8" + (", " + norms if norms else "")
                return "HIGH", names, norms, max(combined_confidence, 80)
        if possible_minor:
            # Minor indication even without strong ML/regex confidence → treat as HIGH with dedicated norm_tag.
            return "HIGH", "DOB_POSSIBLE_MINOR", "LGPD Art. 14 – possible minor data; GDPR Art. 8", max(combined_confidence, 80)
        if combined_confidence >= 70:
            if entertainment_context:
                # ML-only confidence in entertainment context (lyrics/tabs) → cap at MEDIUM so that
                # these cases surface for human review without overwhelming the report with HIGH.
                return "MEDIUM", "ML_POTENTIAL_ENTERTAINMENT", "Potential personal data in entertainment context", combined_confidence
            return "HIGH", "ML_DETECTED", "LGPD/GDPR/CCPA context", combined_confidence
        if combined_confidence >= 40:
            return "MEDIUM", "ML_POTENTIAL", "Potential personal data", combined_confidence
        return "LOW", "GENERAL", "Non-personal", combined_confidence
