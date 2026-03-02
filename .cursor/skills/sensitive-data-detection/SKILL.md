---
name: sensitive-data-detection
description: Guides Python3 programs that access databases and filesystems to detect possible personal or sensitive data using regex and ML, aligned with LGPD, GDPR and similar norms. Use when implementing or reviewing PII/sensitive data detection, compliance scanning, crawlers, or pattern recognition for data protection laws.
---

# Sensitive Data Detection (Python3, DB, Filesystem, ML, Regex)

Guidance for building or reviewing tools that find possible personal or sensitive data in databases and filesystems, using regex, ML, and regulatory alignment.

## When to Apply This Skill

- Implementing scanners/crawlers for PII or sensitive data
- Designing regex or ML classifiers for compliance (LGPD, GDPR, CCPA)
- Reading/writing DB or filesystem with data protection in mind
- Reviewing or refactoring detection logic

## Core Stack

| Concern | Preferred approach | Notes |
|--------|--------------------|--------|
| **Regex** | `re` with compiled patterns for hot paths | Prefer `re.compile()` when same pattern is used repeatedly |
| **DB access** | Parameterized queries only; never concatenate user input into SQL | Use DB-API placeholders or ORM |
| **Filesystem** | `pathlib` for paths; stream large files; avoid loading entire file into memory when unnecessary |
| **ML** | TF-IDF + classifier (e.g. RandomForest) or similar for semantic “is this field name/context sensitive?” | Use for labels/column names/context; combine with regex for value checks |

## Detection Strategy

1. **Regex first** for known formats (CPF, CNPJ, email, phone, SSN, credit card, dates of birth). Use patterns that match *structure*; validate checksum when required (e.g. CPF).
2. **ML second** for context: column names, field labels, file names, log messages. Train or prompt on “sensitive vs non-sensitive” examples (e.g. LGPD/GDPR taxonomy).
3. **Classify and tag** each finding with a *data category* and, when possible, a *legal basis* (e.g. “personal data – LGPD Art. 5”, “sensitive – LGPD Art. 5 II”) so reports support compliance.

## Regex Conventions

- Use raw strings (`r"..."`) for patterns.
- Prefer **bounded** patterns (e.g. `\b`, `^`, `$` or explicit delimiters) to reduce false positives.
- Keep a single source of patterns (e.g. a `RegexPatterns` class or module) and reference it from scanner and report code.
- Document which regulation or norm each pattern supports (e.g. “CPF – LGPD personal data”).

Example pattern set (extend per project):

```python
# Brazilian identifiers (LGPD-relevant)
CPF = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
CNPJ = r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"

# International / generic
EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
PHONE_BR = r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b"
DATE_DMY = r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
```

## Database Access

- **Scanning**: Use parameterized queries to list tables/columns (e.g. `information_schema`) and to sample or search content; never build SQL with string formatting of user/content.
- **Connections**: Prefer context managers and connection pooling; avoid storing credentials in code (env vars or secret manager).
- **Result handling**: Iterate cursors or use chunking for large result sets; avoid loading full tables into memory when not needed.

## Filesystem Access

- **Paths**: Use `pathlib.Path`; normalize and resolve when comparing or logging.
- **Traversal**: Respect symlinks and recursion limits; skip directories that should be excluded (e.g. `.git`, `node_modules`, virtualenvs).
- **Content**: For text, open with encoding (e.g. `encoding='utf-8'`, `errors='replace'`); for binary, use regex on decoded chunks or dedicated parsers (e.g. PDF, Office) as needed.

## ML for “Sensitive or Not”

- **Input**: Field/column names, labels, or short context strings (e.g. “data_nascimento”, “customer_email”).
- **Output**: Binary or probability (sensitive vs non-sensitive) to combine with regex. Optionally multi-label (e.g. “personal”, “sensitive”, “non-personal”).
- **Training**: Include examples from LGPD/GDPR/CCPA terminology (personal data, sensitive data, identifiers, health, biometrics, etc.) and clear non-sensitive examples (IDs, aggregates, system logs).
- **Inference**: Use the same vectorizer and feature pipeline as training; persist model and vectorizer for production.

## Regulatory Mapping

Tag findings with at least:

- **Category**: e.g. personal data, sensitive personal data, anonymous/aggregate.
- **Norm** (optional but recommended): e.g. “LGPD Art. 5”, “GDPR Art. 4(1)”, “CCPA personal information”.

This supports compliance reports and retention/processing rules. For detailed definitions and article references, see [reference.md](reference.md).

## Report and Documentation

- **Findings**: Include location (table/column, file path, line/offset), matched pattern or ML score, category, and suggested norm.
- **Code**: Document which patterns and categories each module implements; keep the mapping between “pattern → category → norm” explicit (e.g. in code comments or a small config).

## Additional Resources

- For regulatory definitions and pattern–norm mapping, see [reference.md](reference.md).
