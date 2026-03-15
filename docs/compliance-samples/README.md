# Compliance samples

**Português (Brasil):** [README.pt_BR.md](README.pt_BR.md)

Sample configuration files to enable **additional compliance frameworks** with the same scan-and-report flow. Copy the relevant blocks into your main config, or set `regex_overrides_file` / `ml_patterns_file` and merge the sample’s `report.recommendation_overrides`. For how to use and how each framework maps to config, see [COMPLIANCE_FRAMEWORKS.md](../COMPLIANCE_FRAMEWORKS.md) ([pt-BR](../COMPLIANCE_FRAMEWORKS.pt_BR.md)).

## Sample files (one per regulation)

| File                               | Purpose                                                                                                        |
| ------                             | ---------                                                                                                      |
| **compliance-sample-uk_gdpr.yaml** | UK GDPR (UK post-Brexit + EU-like): norm_tag and recommendation overrides aligned with ICO and UK provisions.  |
| **compliance-sample-pipeda.yaml**  | PIPEDA (Canada, federal private sector): personal information, consent, and Canadian identifiers (e.g. SIN).   |
| **compliance-sample-popia.yaml**   | POPIA (South Africa): responsible party, personal information, and SA identifiers.                             |
| **compliance-sample-appi.yaml**    | APPI (Japan): personal information and retained personal data; terms and overrides for PPC alignment.          |
| **compliance-sample-pci_dss.yaml** | PCI-DSS (payment card data): card/financial patterns and recommendation overrides for merchants and assessors. |

These files will be added in the next phases. Each sample is self-contained (regex overrides, ML terms, recommendation overrides) so you can enable one framework by including that file’s blocks in your config.
