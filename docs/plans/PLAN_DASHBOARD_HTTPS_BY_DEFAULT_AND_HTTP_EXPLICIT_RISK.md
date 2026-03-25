# Plan: Dashboard HTTPS-by-default with explicit HTTP risk mode

**Status:** Not started
**Synced with:** [PLANS_TODO.md](PLANS_TODO.md)

## Purpose

Make dashboard traffic **encrypted by default** (TLS >= 1.2) even without an upstream reverse proxy/load balancer, while preserving a deliberate HTTP mode for constrained environments with strong warnings and explicit operator responsibility.

## Why this matters

- Prevent accidental plaintext dashboard traffic on internal networks.
- Keep secure-by-design posture independent of external infra quality.
- Preserve compatibility with existing deployments behind reverse proxy / load balancer.
- Improve compliance/legal narrative with explicit secure defaults and auditable opt-out.

## Scope and boundaries

| In scope | Out of scope |
| --- | --- |
| Native HTTPS listener option for dashboard app (TLS >= 1.2 baseline) | Replacing upstream WAF/reverse-proxy hardening responsibilities |
| Redirect or force behavior toward HTTPS by default | Full PKI lifecycle automation beyond practical local cert handling |
| Explicit HTTP opt-in flag with risk warnings and audit trail | Claiming transport-security compliance by itself |
| UI banner + logs + status/health + audit signals for insecure mode | Eliminating ability to run HTTP in all environments |

## Target behavior (operator experience)

1. **Default posture:** dashboard starts in HTTPS-capable mode (either direct TLS or explicit requirement that TLS is enabled in config/flags).
1. **Unsafe override:** operator must explicitly pass an HTTP flag (example: `--allow-insecure-http`) to run plaintext.
1. **Clear warnings:** startup stdout/stderr + logs + API health/status + dashboard banner show that traffic is not cryptographically protected in insecure mode.
1. **Audit visibility:** scan/session or runtime audit surfaces indicate insecure dashboard transport when enabled.
1. **Reverse proxy compatibility:** app still works correctly when TLS is terminated upstream; docs keep this as recommended enterprise pattern.

## Proposed implementation phases

| Phase | To-do | Status |
| --- | --- | --- |
| 1. Transport config and flags | Add explicit dashboard transport mode (`https`, `http`), cert/key parameters, and insecure override flag (`--allow-insecure-http` style). Keep backwards-compatible defaults during rollout with deprecation warning path. | ⬜ Pending |
| 2. Runtime enforcement and warnings | Enforce secure default behavior; on insecure override, print unmistakable warning on stdout/stderr and structured log fields (`transport_security=insecure_http`). | ⬜ Pending |
| 3. UX warning surfaces | Add high-visibility dashboard banner (top half area) for insecure mode and surface same state in API `/status` and health output. | ⬜ Pending |
| 4. Audit trail and evidence | Record insecure transport mode in audit trail / exported audit JSON so risk acceptance is traceable. | ⬜ Pending |
| 5. Tests (both scenarios) | Add tests for HTTPS mode and HTTP override mode, including warning text, status flags, and banner rendering. Keep CI stable and deterministic. | ⬜ Pending |
| 6. Docs and legal/compliance wording | Update USAGE/TECH_GUIDE/SECURITY (+ pt-BR), COMPLIANCE_AND_LEGAL wording, and operator runbooks with concrete setup and risk statements. | ⬜ Pending |

## Concrete technical checklist

1. Add transport args/config:
   - `--https-cert-file`, `--https-key-file` (or equivalent config keys).
   - `--allow-insecure-http` (explicit risk acceptance).
   - Optional `--https-port` and redirect behavior if dual-port is supported.
1. Force clear startup messaging:
   - Secure mode: “Dashboard transport: HTTPS (TLS>=1.2 expected)”.
   - Insecure mode: multi-line warning including interception risk.
1. Add machine-readable indicators:
   - `/status` and health include transport mode + security level.
   - structured logs include `dashboard_transport_mode`.
1. Add UI warning banner:
   - visible in dashboard header/top half while insecure mode is active.
1. Extend tests:
   - unit tests for flag parsing and warning paths.
   - API/status tests for security-state fields.
   - dashboard rendering test for insecure banner.

## Rollout strategy

- **Step A (safe introduction):** add feature behind explicit flags and status signals.
- **Step B (default tightening):** switch docs and startup defaults to HTTPS-first.
- **Step C (legacy assist):** keep insecure flag available with strong warnings for controlled exceptions.

## Risks and mitigations

- Risk: cert/key setup friction for local labs.
  - Mitigation: provide minimal local certificate quickstart and clear fallback with warning.
- Risk: false sense of security if users rely only on app TLS.
  - Mitigation: docs state reverse proxy/network controls still recommended.
- Risk: CI instability with TLS tests.
  - Mitigation: deterministic local cert fixtures and scoped tests.

## Notes for roadmap/pitch/legal

- **Compliance/legal docs:** good candidate for a short statement about secure transport by default + explicit insecure override risk.
- **Decision-maker pitch:** optional short mention only after baseline implementation lands (avoid promising before behavior is shipped).
