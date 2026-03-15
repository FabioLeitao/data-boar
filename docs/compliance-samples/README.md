# Compliance samples

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

Sample configuration files to enable **additional compliance frameworks** with the same scan-and-report flow. Copy the relevant blocks into your main config, or set `regex_overrides_file` / `ml_patterns_file` and merge the sample’s `report.recommendation_overrides`. For how to use and how each framework maps to config, see [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md) ([pt-BR](../COMPLIANCE_FRAMEWORKS.pt_BR.md)).

## Sample files (one per regulation)

| File                               | Purpose                                                                                                                                                    |
| ------                             | ---------                                                                                                                                                  |
| **compliance-sample-lgpd.yaml**    | LGPD (Brazil): bilingual PT-BR + EN terms (e.g. documento oficial / official document, RG, CNH / Driver License); RG/CEP regex; for Brazilian deployments. |
| **compliance-sample-uk_gdpr.yaml** | UK GDPR (UK post-Brexit + EU-like): norm_tag and recommendation overrides aligned with ICO and UK provisions.                                              |
| **compliance-sample-eu_gdpr.yaml** | EU GDPR (EEA): EU 2016/679 Art. 4(1), EDPB, member-state DPAs; optional EN + DE/FR terms.                                                                   |
| **compliance-sample-benelux.yaml** | Benelux (BE, NL, LU): EU GDPR base + national IDs (BSN, NISS, Luxembourg ID) and national DPA overrides; EN + NL/FR terms.                                  |
| **compliance-sample-pipeda.yaml**  | PIPEDA (Canada, federal private sector): personal information, consent, and Canadian identifiers (e.g. SIN).                                               |
| **compliance-sample-popia.yaml**   | POPIA (South Africa): responsible party, personal information, and SA identifiers.                                                                         |
| **compliance-sample-appi.yaml**    | APPI (Japan): personal information and retained personal data; terms and overrides for PPC alignment.                                                      |
| **compliance-sample-pci_dss.yaml** | PCI-DSS (payment card data): card/financial patterns and recommendation overrides for merchants and assessors.                                             |

**compliance-sample-lgpd.yaml** and **compliance-sample-uk_gdpr.yaml** are available; EU GDPR, Benelux, PIPEDA, POPIA, APPI, and PCI-DSS will be added in later phases. Each sample is self-contained (regex overrides, ML terms, recommendation overrides) so you can enable one framework by including that file's blocks in your config.

### Language and target audience

When choosing or authoring a sample, consider the **language(s)** of the target region so column names and labels in data are detected:

| Regulation / region      | Recommended language(s) for terms and labels                                                                   |
| -------------------      | ---------------------------------------------                                                                  |
| **LGPD (Brazil)**        | Portuguese (BR) and English (e.g. "documento oficial" and "official document", "CNH" and "Driver License").    |
| **PIPEDA (Canada)**      | English and French (e.g. "personal information" and "renseignements personnels") where scanning Canadian data. |
| **UK GDPR**              | English.                                                                                                       |
| **EU GDPR (EEA)**        | English; optional German/French for multilingual EU data.                                                    |
| **Benelux (BE, NL, LU)** | English plus Dutch and/or French (e.g. BSN, NISS, national ID column names).                                   |
| **POPIA (South Africa)** | English; add local languages in terms if your data uses them.                                                  |
| **APPI (Japan)**         | Japanese and/or English as needed for column names.                                                            |
| **PCI-DSS**              | English.                                                                                                       |

Document in the sample header or in [COMPLIANCE_FRAMEWORKS](../COMPLIANCE_FRAMEWORKS.md) when a sample includes multi-language terms. See also the rule **.cursor/rules/compliance-samples-language.mdc**.

**For authors:** Use **double-quoted** YAML for regex `pattern` values with **escaped backslashes** (e.g. `pattern: "\\b[A-Z]{2}\\s?\\d{6}\\s?[A-D]\\b"`). This avoids "Invalid escape sequence" linter errors and loads correctly; the value passed to the regex engine is `\b`, `\s`, `\d` as intended. Do not use single-quoted or unescaped `\d`/`\s` in double quotes. Tests in `tests/test_compliance_samples.py` validate structure and that the detector loads each sample.
