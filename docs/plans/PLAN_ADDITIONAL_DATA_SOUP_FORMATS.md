# Plan: Additional "data soup" formats and rich media

**Status:** Tier 3 **metadata + subtitles + magic-byte cloaking** — **merged to `main` when shipped** (see [PLANS_TODO.md](PLANS_TODO.md) **Integration / WIP** until then); Tier 1 formats and **stego** remain backlog (see to-dos below).
**Synced with:** [PLANS_TODO.md](PLANS_TODO.md)

**Related plans:** [PLAN_COMPRESSED_FILES.md](PLAN_COMPRESSED_FILES.md) (scan inside archives), [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md) (magic-byte/cloaking), [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md#steganography-future--optional) (steganography as future phase).

This plan catalogues **additional file formats** that are often present in production and could become "data soup ingredients"—either as **first-class scan targets** (we extract text/structure and run sensitivity detection), as **members inside compressed files** (covered by the compressed-files plan), as **cloaked/renamed files** (covered by the content-type plan), or as **containers for steganography** (images, audio, video where data may be hidden). The goal is to have a single place to prioritise and design format additions and to align with compressed, cloaking, and stego work.

---

## How formats can show up in production

1. **On disk or share (by extension):** We already support many text and document formats; see `SUPPORTED_EXTENSIONS` in the filesystem connector. Gaps below.
1. **Inside compressed files:** When [PLAN_COMPRESSED_FILES](PLAN_COMPRESSED_FILES.md) is implemented, we will see **inner members** with various extensions (e.g. `.csv`, `.xlsx`, `.pdf` inside `.zip`). The same format list and extractors apply; no extra format work unless we add a **new** format we don’t yet support.
1. **Cloaked or renamed:** A file may have a misleading extension (e.g. `.pdf` renamed to `.txt`). [Content-type / cloaking](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md) uses magic bytes to detect the real type and scan accordingly. Again, the set of formats we can **extract** is the same; the plan just ensures we recognise them when extension is wrong.
1. **Steganography:** Data can be **hidden inside** images (e.g. PNG, JPEG, BMP), **audio** (WAV, MP3, FLAC), or **video** (MP4, AVI). The "file" is a valid image/audio/video, but extra payload is embedded. Detecting or extracting that is a **separate, compute-heavy** capability (stego detection tools, entropy analysis). This plan treats **rich media as potential stego containers** and lists them so we can later add an optional "scan for hidden content" phase without forgetting formats.

---

## Default vs opt-in

| Category                                                                        | Recommendation                                            | Rationale                                                                                                                                                                                                             |
| --------                                                                        | --------------                                            | ---------                                                                                                                                                                                                             |
| **Tier 1 – New document/data formats** (epub, parquet, avro, dbf, orc, feather) | **Default** (no new CLI/web flag)                         | Same pattern as current PDF/XLSX: one read, extract sample, run detector. No extra full-disk scan; only more extensions in `SUPPORTED_EXTENSIONS`. Memory: bounded by existing `sample_limit` and row/chunk sampling. |
| **Tier 3 – Metadata-only** (EXIF, ID3, video tags/subtitles)                    | **Default** (or single opt-in "Scan rich-media metadata") | One read of metadata block; no decoding of full image/audio. Very low compute. If we ever add many metadata sources, one config/CLI flag (e.g. `file_scan.scan_rich_media_metadata: true`) keeps it toggleable.       |
| **Tier 3 – Steganography** (detect/extract hidden data in images, audio, video) | **Opt-in** (CLI + web)                                    | Heavy: stego tools, entropy analysis, per-file decode. Must be behind e.g. `file_scan.scan_for_stego` and `--scan-stego` / dashboard checkbox, with docs warning about I/O and CPU.                                   |

**Conclusion:** Add new Tier 1 formats as **default** behaviour (extend `_TEXT_EXTENSIONS` / `_DOCUMENT_EXTENSIONS` / `_DATA_EXTENSIONS` and `_read_text_sample` in the filesystem connector). Add **stego** only as **opt-in** with CLI arg and web option; document resource impact.

---

## Tier 1: Formats we could add as first-class (extract text/structure)

These are common in production and would need an **extractor** in `_read_text_sample` (or equivalent) so we can run sensitivity detection on extracted text or metadata. They are **not** stego-specific; they are "normal" formats we don’t yet support.

| Extension(s)             | Format / use in production                    | Notes / effort                                                                  | Corporate relevance                                  |
| ----------------         | --------------------------------------------- | ------------------------------------------------------------------------------  | -------------------                                  |
| `.epub`                  | E-book (ZIP-based; OCF)                       | Unzip, parse container.xml + content documents (XHTML); extract text. Moderate. | Training materials, compliance docs, policy e-books. |
| `.mobi`, `.azw3`         | Kindle / e-book                               | Opaque format; libs exist (e.g. calibre, mobi); effort higher.                  | Less common in corporate; optional.                  |
| `.parquet`               | Columnar data (Spark, DWH, data lakes)        | Read schema + optional sample; pyarrow. Metadata and column names; sample rows. | Data lakes, analytics, Spark/Hadoop exports.         |
| `.avro`                  | Row/column (Hadoop, Kafka, data pipelines)    | Schema + sample; fastavro or avro. Similar to parquet.                          | Event streams, Kafka, data pipelines.                |
| `.orc`                   | Apache ORC (columnar, Hive/Spark)             | pyarrow; schema + sample rows. Same pattern as Parquet.                         | Data lakes, Hive, Spark exports.                     |
| `.feather`               | Arrow Feather (pandas/pyarrow interchange)    | pyarrow or pandas.read_feather; trivial.                                        | Fast columnar interchange between services.          |
| `.dbf`                   | Legacy dBase / FoxPro (still in some sectors) | dbfread or pandas; small addition.                                              | Legacy gov, finance, municipal systems.              |
| `.ods` / `.odt` / `.odp` | ODF (we have ODF in code)                     | Already in SUPPORTED; ensure extractors are robust.                             | Cross-platform office docs.                          |
| `.numbers`               | Apple Numbers (optional, macOS/iCloud)        | ZIP-based or proprietary; lower priority unless requested.                      | macOS/iCloud shops; lower priority.                  |
| `.key`                   | Apple Keynote                                 | Similar; lower priority.                                                        | macOS/iCloud; lower priority.                        |
| `.pages`                 | Apple Pages                                   | Similar; lower priority.                                                        | macOS/iCloud; lower priority.                        |

**Recommendation:** Prioritise **.epub** (ZIP-based, straightforward), **.parquet** / **.avro** / **.orc** / **.feather** (common in data platforms; Parquet/ORC/Feather require `pyarrow`—add to optional extra `[dataformats]` or main deps by product decision). .dbf is low effort. .mobi/.azw3 and Apple formats can follow if needed.

---

## Tier 2: Formats reached via other plans (no new extractor)

These are either **already supported** or will be **reached** by compressed-file scan or content-type detection. We only need to **list them** so operators know they’re covered (or will be).

- **Inside archives:** Any format we already support (.txt, .csv, .pdf, .docx, .xlsx, …) will be scanned when it appears **inside** a .zip, .tar.gz, .7z, etc. once [PLAN_COMPRESSED_FILES](PLAN_COMPRESSED_FILES.md) is done. Password-protected archives: use `file_passwords` (reminder in that plan).
- **Cloaked:** Once [content-type detection](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md) is on, a file renamed to the wrong extension (e.g. .pdf → .txt) will be detected by magic bytes and scanned as PDF. No new format; same extractors.
- **Legacy Office / text we already support:** .doc (binary; we currently return empty but path/name still analysed), .rtf, .csv, .xml, .html, etc. Improvements to .doc extraction could be a small follow-up.

---

## Tier 3: Rich media as stego containers (images, audio, video)

In production, **images**, **audio**, and **video** files are common. We do **not** currently extract text from them (no OCR, no transcription). They are relevant here for two reasons:

1. **Metadata:** Some formats carry metadata (EXIF, ID3, XMP, subtitle tracks) that might contain PII or sensitive strings. We could add **metadata-only** extraction (e.g. read EXIF, ID3, subtitle file paths) as a **lightweight** addition without full stego.
1. **Steganography:** Data can be **hidden** inside image/audio/video payloads. Detecting or extracting hidden content requires dedicated tools (e.g. stegano, steghide, entropy analysis) and is **compute- and I/O-intensive**. This plan treats stego as a **future optional phase** (as in the content-type plan): list the **container formats** we might eventually support for stego so we don’t forget them.

### Image formats (potential stego containers)

| Extension(s)                             | Common in production      | Notes                                                                 |
| --------------                           | ------------------------- | --------------------------------------------------------------------- |
| `.png`, `.jpg`, `.jpeg`                  | Very common               | Primary targets for image stego. JPEG (DCT), PNG (chunks).            |
| `.gif`, `.bmp`, `.webp`, `.tiff`, `.tif` | Common                    | Also used for stego. BMP simple; TIFF can have many layers.           |
| `.heic`, `.heif`                         | Growing (mobile/Apple)    | Same idea; lib support varies.                                        |

**Today:** We could add **metadata-only** (EXIF, XMP) for images without implementing stego. That gives some value (camera owner, GPS, etc.) with low effort. **Stego:** Optional later phase; document as "possible future" and gate behind an opt-in (e.g. `file_scan.scan_images_for_stego`).

### Audio formats (potential stego containers)

| Extension(s)                                    | Common in production                          | Notes                                                                 |
| --------------                                  | -------------------------                     | --------------------------------------------------------------------- |
| `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`, `.aac` | Very common (recordings, podcasts, voicemail) | Audio stego hides data in samples or unused bits.                     |
| `.wma`, `.ape`                                  | Less common                                   | Same idea.                                                            |

**Today:** We could add **metadata-only** (ID3, etc.) for audio. **Stego:** Optional later phase; document and gate behind opt-in.

### Video formats (potential stego containers)

| Extension(s)                                    | Common in production                        | Notes                                                                 |
| --------------                                  | -------------------------                   | --------------------------------------------------------------------- |
| `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.webm` | Very common (recordings, exports, training) | Video can carry stego in frames or in container metadata/subtitles.   |

**Today:** Metadata (e.g. title, tags) and **subtitle tracks** (e.g. .srt, .vtt inside or alongside) could be scanned as text without full stego. **Stego:** Optional later phase.

### Tier 3b: Embedded trackers / “tracking pixels” (Meta, TikTok, and similar)

**Context:** External security commentary (e.g. Security Now) highlights that **rich media** (images, video, some document exports) can embed or reference **third-party tracking endpoints** used by large platforms (e.g. Meta/Facebook, TikTok). That is relevant to Data Boar because operators may need to know whether **files in scope** contain references that could support **cross-site or cross-app tracking** or **telemetry**, which may intersect with **privacy and sensitive-data governance** (especially when combined with other findings).

## Product intent (planned, not implemented until sliced):

1. **Detection (heuristic):** When scanning supported rich-media paths, optionally look for **known tracker URL patterns or hostnames** (e.g. `facebook.com/tr`, `connect.facebook.net`, TikTok-related endpoints) in:
   - extracted **metadata** strings,
   - **subtitle / sidecar** text where applicable,
   - **lightweight binary/string passes** on container payloads where safe and bounded (no full decode of every frame by default).
1. **Opt-in by default:** Same posture as **compressed archive scan** and **heavy stego** — **off** unless the operator explicitly enables it:
   - **CLI:** e.g. `--scan-tracking-pixels` (name TBD; document next to `--scan-compressed` / content-type flags).
   - **Config:** e.g. `file_scan.scan_embedded_trackers: false` (default false).
   - **Dashboard:** optional checkbox; if runtime cost is high on large trees, **keep off by default** and document CPU/I/O impact (similar to compressed scan warnings).
1. **Outputs when findings exist:**
   - **Report:** dedicated row/section or sheet column (e.g. “embedded tracker references”) with **count + sample context** (redacted if needed).
   - **Operator surfaces:** at least **WARNING** to **stdout**, **stderr**, and **application log** so unattended runs and CI still see the signal.
1. **Licensing (future):** Candidate for **enterprise / advanced** entitlement in `LICENSING_SPEC.md` (feature flag + doc-only until product decides). Not a commitment to ship as paid-only until validated.

**Dependencies:** Builds on existing **Tier 3 rich media** metadata/subtitle paths; does not require full video decode for a **first slice** (string/metadata heuristics first). Link: [SECURITY_INSPIRATION_GRC_SECURITY_NOW.md](../ops/SECURITY_INSPIRATION_GRC_SECURITY_NOW.md).

**Program umbrella:** Treat **Tier 3b** as the **network/telemetry string** slice of a larger **“sniffing for hidden ingredients”** track—together with **Tier 4** (document tricks) and **stego** (payload hiding). One phased roadmap avoids promising a single “magic toggle” that does everything.

**Live host / port hints (optional, allowlisted):** For **operator-declared** hosts and well-known ports—**bounded** TCP connect + short banner read, not a stealth scanner—see [PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md](PLAN_OPT_IN_NETWORK_PORT_SERVICE_HINTS.md). Complements Tier 3b (strings **inside** files) by surfacing **possibly relevant listeners** the customer did not add as formal targets.

---

## Tier 4: Document-layer “hidden ingredients” and surveillance-adjacent signals (taxonomy / backlog)

This section raises **“ingesting and digesting the data soup”** and **“sniffing for hidden ingredients”** to a **design level**: catalogue patterns that often evade casual search but may matter for **privacy, integrity, or governance** reporting. **None of this implies the product already performs every check**—each row should move through **PLANS_TODO**, **USAGE**, and tests when implemented.

### A. Visibility and human-perception tricks (office documents, PDFs, exports)

| Pattern                                        | What it is                                              | Why it matters                                        | Product direction (when sliced)                                                                                       |
| -------                                        | ----------                                              | --------------                                        | -------------------------------                                                                                       |
| **Microscopic or minimally sized text**        | Font sizes near readability threshold, text in margins  | Can hide IDs, watermarks, legal text, or instructions | Heuristics on extracted layout/text stats + optional “suspicious density” flags in report                             |
| **Low-contrast / same-color text**             | White-on-white, near-identical foreground/background    | Deliberate concealment or bad export hygiene          | Where extractors expose spans/colors (PDF/advanced DOCX), flag **anomaly** buckets; otherwise document as limitation  |
| **Off-page or clipped content**                | Text boxes outside printable area, negative coordinates | Common in sloppy templates; sometimes abuse           | Layout-aware parsers where available; “out-of-bounds text” warning class                                              |
| **Hidden rows/columns/sheets**                 | Excel/ODS hidden sheets or very narrow columns          | May hold PII or cross-walk tables                     | Already partially visible via structure reads; extend with explicit **hidden sheet/column** reporting where supported |
| **Collapsed outline / grouped rows**           | Content folded in UI but present in file                | Operators may miss in manual review                   | Surface **structural** hints in metadata/findings when connector exposes them                                         |
| **Comments, revision history, embedded notes** | Author comments, track-changes residue                  | Often rich in PII and informal language               | Continue to prioritize extractors that include comments/tracked changes in sample or dedicated pass                   |

### B. Character- and encoding-level cloaking

| Pattern                                            | What it is                | Why it matters                                                         | Product direction                                                                     |
| -------                                            | ----------                | --------------                                                         | -----------------                                                                     |
| **Zero-width / bidirectional override characters** | ZWJ, ZWNJ, RLO, etc.      | Can break naive search, smuggle fingerprints, or obfuscate identifiers | Optional normalisation pass + report “non-printing density” / suspicious Unicode runs |
| **Homoglyphs / confusable glyphs**                 | Cyrillic “а” vs Latin “a” | Evasion against keyword lists                                          | Optional homoglyph normalisation for **selected** detection passes (config-gated)     |
| **Whitespace padding / fragmented tokens**         | `C P F` split across tags | Weakens regex unless normalised                                        | Already partially handled where text is flattened; extend per connector               |

### C. Steganography and covert channels (cross-reference)

| Area                              | Note                                                                                                                                                        |                                                                                                                      |
| ----                              | ----                                                                                                                                                        |                                                                                                                      |
| **Images, audio, video payloads** | Covered in **Tier 3** and [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md). Remains **opt-in** and compute-heavy. |                                                                                                                      |
| **Polyglot files**                | Single file valid as two types; may bypass extension or magic-byte assumptions                                                                              | Align with **content-type** and archive plans; optional “polyglot suspicion” only with strong signals to avoid noise |

### D. Network- and tracking-adjacent strings inside documents

| Pattern                                               | What it is                                                                                             | Why it matters                                                          | Product direction                                                                                             |
| -------                                               | ----------                                                                                             | --------------                                                          | -----------------                                                                                             |
| **Web bugs / tracker URLs**                           | Single-pixel, analytics endpoints in HTML, SVG, email HTML                                             | Cross-context tracking, leakage of open/read behaviour                  | Overlap with **Tier 3b**; extend host/path allow deny lists per operator policy                               |
| **Marketing-automation and ESP endpoints**            | Marketo, HubSpot, Mailchimp, SendGrid, Braze-style image/beacon URLs in exports                        | Correlates opens/clicks to individuals when combined with mailing lists | Same heuristic bucket as Tier 3b; optional **category** tag in report (not a legal verdict)                   |
| **Ad / social SDKs and widgets**                      | `googletagmanager`, `doubleclick`, LinkedIn Insight, Twitter/X widgets, Reddit pixels (evolving hosts) | Cross-site profiles; compliance “unknown unknowns” in leaked exports    | Expandable host list + **versioned** pattern pack; heavy dependence on updates—document maintenance cost      |
| **Link shorteners and redirect chains**               | `bit.ly`, `t.co`, branded short domains                                                                | Obscures final destination; may hide tracker landings                   | Optional **resolve** step only when operator enables and timeout budget allows; else flag **opaque URL** only |
| **UTM and campaign parameters only**                  | `utm_source`, `utm_campaign`, `fbclid`, `gclid`                                                        | Not always PII; signals **intentional campaign plumbing**               | Low-noise reporting: **campaign plumbing detected** exposure class                                            |
| **Fingerprint / analytics JS snippets in saved HTML** | Inline scripts referencing known FingerprintJS-like or cohort hints                                    | Surveillance-adjacent in customer-owned archives                        | String heuristic only unless product explicitly adds JS parsing (later)                                       |
| **Deep links / deferred attribution**                 | Universal links, app-specific URL schemes                                                              | May join file content to ad/attribution networks                        | Heuristic URL inventory + optional framework tags (not legal conclusions)                                     |
| **License / asset URLs in creative**                  | Stock, font, template CDNs                                                                             | Operational metadata; sometimes sensitive in insider contexts           | Low-cost string extraction already; categorise in report as **provenance** where useful                       |

### E. Embedded objects and compound documents

| Pattern                                        | What it is            | Why it matters                                     | Product direction                                   |
| -------                                        | ----------            | --------------                                     | -----------------                                   |
| **OLE packages, attached files inside Office** | Nested payloads       | Bypass perimeter that only lists “top-level” files | Archive/compound-document plan: recurse with bounds |
| **PDF attachments / portfolios**               | Files embedded in PDF | Same as above                                      | Parser support + size/time limits                   |

### F. Machine-readable “ingredients” in visual form

| Pattern                             | What it is         | Why it matters                                           | Product direction                                                                                                         |
| -------                             | ----------         | --------------                                           | -----------------                                                                                                         |
| **Barcodes, QR codes in documents** | Encoded PI or URLs | OCR/vision stack may decode; sensitive if payload is PII | Optional decode path aligned with existing **scan_image_ocr** posture; report as **encoded payload** with redaction rules |

### G. Steganography and entropy-style “maybe hidden” (cross-reference, not duplicate spec)

| Pattern                                           | What it is                                | Why it matters                                                                         | Product direction                                                                            |
| -------                                           | ----------                                | --------------                                                                         | -----------------                                                                            |
| **LSB / transform-domain hiding**                 | Classic image/audio/video stego           | Illicit exfil or watermarking; rare in routine compliance but high impact when present | **Opt-in** `--scan-stego` (or equivalent); bounded tools; see Tier 3 stego rows              |
| **Unused / reserved chunks**                      | PNG ancillary chunks, APP markers in JPEG | Sometimes misused for payload                                                          | Parser-specific; only with explicit stego phase                                              |
| **High-entropy segments in “beneath” containers** | Appended data after EOF, polyglot tricks  | May indicate tooling abuse                                                             | Align with **polyglot** and **content-type** plans; avoid noisy global entropy on every file |

Tier **G** stays **light in this doc**: implementation detail belongs in [PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md](PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md) stego subsection and in `file_scan.scan_for_stego` when that ships.

### Reporting and “exposure” narrative (design target)

When features land, prefer a **consistent story** in Excel and operator logs:

1. **Exposure class** — e.g. `hidden_structure`, `tracker_reference`, `campaign_plumbing`, `opaque_redirect`, `stego_suspect`, `unicode_obfuscation`, `embedded_object`, `encoded_graphic`.
1. **Severity / review band** — tie to existing sensitivity and “review band” patterns so legal/compliance language stays stable.
1. **Evidence budget** — short **sample** or hash of location, not bulk exfiltration of payload; align with “metadata only” promise in [COMPLIANCE_AND_LEGAL.md](../COMPLIANCE_AND_LEGAL.md).
1. **Operator opt-in** — heavy or ambiguous checks stay behind flags to protect I/O, false positives, and licensing posture.

---

## Dependencies and order

- **Parquet / ORC / Feather:** Require **pyarrow**. Add to optional extra `[dataformats]` in pyproject.toml (e.g. `pyarrow>=14.0.0`) or to main dependencies by product decision. When missing, skip these extensions with a clear reason or document that installing `.[dataformats]` enables them.
- **Compressed files:** When implemented, **inner** files with any of the Tier 1 formats (once we add extractors) will be scanned automatically. Password-protected archives: see PLAN_COMPRESSED_FILES.
- **Content-type / cloaking:** When implemented, **renamed** Tier 1 (and existing) formats will be recognised by magic bytes and scanned. No new format list needed for cloaking.
- **Steganography:** Depends on having a clear list of **container** formats (images, audio, video) and on an **opt-in** flag so we don’t run heavy stego by default. Can follow after Tier 1 format additions and after content-type if desired.

Suggested order:

1. Implement **compressed files** and **content-type** as already planned (no new formats required for basic coverage).
1. Add **Tier 1** formats (epub, parquet, avro, orc, feather, dbf) as first-class **default** behaviour so they are scanned on disk, in shares, and **inside archives** once compressed is on. No new CLI/web flag for Tier 1.
1. Optionally add **metadata-only** for images/audio/video (EXIF, ID3, subtitles) for low-effort coverage; default or single opt-in flag.
1. **Steganography** as a separate, **opt-in** phase: CLI `--scan-stego`, web/dashboard option, config `file_scan.scan_for_stego`; document container list (this plan) and resource impact; implement when resources allow.
1. **Tier 3b embedded trackers** (Meta/TikTok-style references): **opt-in** CLI + config + optional dashboard; heuristic pass on rich-media metadata/strings; report + log warnings; see **Tier 3b** section above.
1. **Tier 4 document-layer hiding:** Prioritise patterns from **Tier 4** table with highest corporate signal and lowest false-positive rate (e.g. hidden sheets, comments, Unicode cloaking normalisation, URL/tracker inventory) before expensive layout-colour analysis.

---

## To-dos (backlog; not sequential until we pick a phase)

| #   | To-do                                                                                                                                                                                                | Status                                                                                                                                                            |
| --- | --------------------------------------------------------------------------------------------------------------------------------                                                                     | ------                                                                                                                                                            |
| 1   | **Tier 1 – EPUB:** Add .epub to SUPPORTED_EXTENSIONS; extract text from OCF (ZIP) content documents; run scanner.                                                                                    | ⬜                                                                                                                                                                 |
| 2   | **Tier 1 – Parquet / Avro:** Add .parquet, .avro; read schema + sample rows; run scanner on column names and sample values.                                                                          | ⬜                                                                                                                                                                 |
| 3   | **Tier 1 – ORC / Feather:** Add .orc, .feather; read via pyarrow; run scanner on column names and sample values.                                                                                     | ⬜                                                                                                                                                                 |
| 4   | **Tier 1 – DBF:** Add .dbf; extract column names + sample rows; run scanner.                                                                                                                         | ⬜                                                                                                                                                                 |
| 5   | **Tier 3 – Metadata only:** Optional extractors for image EXIF/XMP, audio ID3, video metadata/subtitles (no stego).                                                                                  | ✅ Done (`file_scan.scan_rich_media_metadata`, `scan_image_ocr`, sidecar `.srt`/`.vtt`/`.ass`/`.ssa`; mutagen/ffprobe/Tesseract optional; see USAGE / TECH_GUIDE). |
| 6   | **Stego phase (future):** Document image/audio/video as stego containers; design opt-in `scan_for_stego`; CLI `--scan-stego` and web/dashboard option; implement or defer.                           | ⬜                                                                                                                                                                 |
| 7   | **Tier 3b – Embedded trackers (Meta/TikTok-style):** Opt-in CLI + config + optional dashboard; heuristic detection in rich media; warnings to stdout/stderr/log + report section; see Tier 3b above. | ⬜                                                                                                                                                                 |
| 8   | **Docs:** When adding formats, update USAGE, TECH_GUIDE, SUPPORTED_EXTENSIONS list; note behaviour inside compressed and when cloaked.                                                               | ✅ Updated for rich media slice; revisit when Tier 1 formats land.                                                                                                 |
| 9   | **Tier 4 – Unicode / cloaking pass:** Config-gated normalisation or reporting for zero-width, bidi, homoglyph risk; integrate with detector sample budget.                                           | ⬜                                                                                                                                                                 |
| 10  | **Tier 4 – Document “hidden structure” signals:** Hidden sheets/columns, out-of-bounds text, low-contrast/micro text where extractors support it; report exposure class.                             | ⬜                                                                                                                                                                 |
| 11  | **Tier 4 – Embedded objects / PDF attachments:** Bounded recursion consistent with compressed-file limits; exposure class `embedded_object`.                                                         | ⬜                                                                                                                                                                 |

**Sync:** When a step is done, update this table and [PLANS_TODO.md](PLANS_TODO.md). This plan remains a **backlog/catalogue** until we prioritise a specific phase.

---

## Summary

- **Production-ready formats we might add:** EPUB, Parquet, Avro, ORC, Feather, DBF (Tier 1); metadata for images/audio/video (Tier 3 lightweight). Tier 1 and metadata-only as **default** (or single opt-in for rich-media metadata); **steganography** always **opt-in** (CLI + web) due to compute/memory.
- **Default vs opt-in:** Tier 1 format additions = default. Stego = opt-in with `--scan-stego` / dashboard and docs on I/O and CPU impact. **Tier 3b embedded trackers** = opt-in (same spirit as compressed scan: off by default, warn when enabled and findings exist).
- **Dependencies:** Parquet/ORC/Feather require pyarrow; add optional extra `[dataformats]` or to main deps by product decision.
- **Already covered by other plans:** Everything we support today will be scanned **inside compressed files** and when **cloaked** once those plans are implemented.
- **Rich media and steganography:** Images, audio, and video are common in production and can carry **hidden data**. We list them as potential stego containers; full stego support is a **future, opt-in** phase to avoid creeping regression and resource exhaustion. **Tier 3** metadata, optional OCR, and subtitle sidecars are **shipped**; see USAGE / TECH_GUIDE.
- **Document-layer hiding (Tier 4):** Taxonomy for microscopic/hidden text, Unicode tricks, embedded objects, and tracker URLs inside exports—**roadmap** for structured exposure reporting; implement incrementally with tests and opt-in where noisy.

---

## Last updated

Plan created. Updated with default vs opt-in section, ORC/Feather in Tier 1, corporate relevance column, pyarrow dependency note, and stego opt-in (CLI + web). **2026-03:** Rich media Tier 3 (metadata OCR, subtitles, magic bytes with `use_content_type`) implemented in code; stego remains explicitly future opt-in. **2026-03-25:** Added **Tier 3b** (optional embedded tracker / tracking-pixel-style heuristics for rich media; Security Now–inspired backlog; opt-in CLI/dashboard; report + log warnings; future licensing note). **2026-03-25:** Added **Tier 4** taxonomy (document-layer hidden ingredients, Unicode cloaking, embedded objects, encoded graphics) and reporting design notes.
