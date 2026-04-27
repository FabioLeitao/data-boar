# ADR 0044: Container image hardening — `databoar` user, read-only rootfs, no package managers

## Context

Data Boar ships a **multi-stage** Docker image (`fabioleitao/data_boar:latest`) and a Compose
stack under [`deploy/docker-compose.yml`](../../deploy/docker-compose.yml). Earlier iterations
already kept `gcc`, `-dev` headers, and `build-essential` out of the runtime stage, but several
"Mission Critical" hardening guarantees were not enforced and could regress silently:

- The runtime user was named `appuser` and `pip` / `wheel` stayed installed in the runtime
  layer for "future maintenance". That re-introduced **Docker Scout** noise on every
  refresh (CVEs against `pip`, `wheel`) without us actually using those tools at runtime.
- The Compose stack did not pin `read_only: true`, `cap_drop: [ALL]`,
  `security_opt: [no-new-privileges:true]`, or `user: "1000:1000"`, so a Swarm or
  k8s deployment could land with a writable rootfs, full Linux capabilities, or — in
  the worst case — a re-rooted container.
- The image declared no **OCI labels** (source, version, license), which makes
  Docker Scout, SBOM correlation, and downstream registry tooling weaker than
  necessary.

The slack mission framing was "Senior DevSecOps / NASA-grade hardening". The doctrinal
seeds for this work live under
[`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
("we are a guest in someone else's environment") and
[`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
(strategy degradation must be monotonic — never silently weaker than declared).

This ADR is **image / runtime hardening only**. It deliberately changes **zero** SQL
sampling, connector, or detector code paths so the "no DB-impact" clause of the
Defensive Scanning Manifesto is preserved. There is no risk of new database locks,
new statement timeouts, or new isolation behaviour from this PR.

## Decision

The container image and the Compose stack adopt the following posture, with regression
tests in [`tests/test_container_hardening.py`](../../tests/test_container_hardening.py)
that block PRs which silently downgrade any of it.

### Dockerfile (`Dockerfile`)

1. **Multi-stage build is mandatory.** The `builder` stage carries `gcc`, `g++`, `-dev`
   headers, and the package manager; the final stage does not.
2. **Final image runs as `databoar` (uid 1000, gid 1000, `/sbin/nologin`).** The legacy
   `appuser` name is replaced. The Compose stack pins the same uid:gid so deployments
   cannot accidentally re-root the process.
3. **`pip`, `pip3`, `pip3.13`, `wheel` binaries and their `site-packages` metadata
   directories are removed from the runtime stage.** Dependencies are already installed
   by the builder stage and copied via `site-packages`. `setuptools` stays because
   some packages still call `pkg_resources` at import time.
4. **`HEALTHCHECK`** is declared in the Dockerfile (hits `/health`), so plain
   `docker run` (no Compose) still surfaces liveness through `docker ps`.
5. **OCI labels** (`org.opencontainers.image.title|description|vendor|source|licenses|version|revision|created`)
   are declared, with build args (`DATA_BOAR_VERSION`, `VCS_REF`, `BUILD_DATE`) so
   `docker buildx` / `docker-lab-build.ps1` can override the defaults at build time.
6. **`PYTHONDONTWRITEBYTECODE=1`** is set in both stages so the runtime filesystem
   stays clean; this is what makes `read_only: true` viable without scattering
   tmpfs entries everywhere.

### Compose (`deploy/docker-compose.yml`)

1. `user: "1000:1000"` — pinned even though the image already drops privileges.
2. `read_only: true` with a `tmpfs: ["/tmp:rw,nosuid,nodev,size=64m"]` mount.
3. `cap_drop: [ALL]` and **no** `cap_add` (the audit container does not need any
   Linux capability to serve HTTP and run read-only sampling).
4. `security_opt: [no-new-privileges:true]`.
5. `pids_limit: 256` and `ulimits.nofile.{soft,hard}` — bounded runtime budget.
   This is a **kernel-side** relief valve in the spirit of §2 of the Defensive
   Scanning Manifesto; it does not replace the application-level caps in
   [`connectors/sql_sampling.py`](../../connectors/sql_sampling.py).
6. The override example at
   [`deploy/docker-compose.override.example.yml`](../../deploy/docker-compose.override.example.yml)
   only swaps the bind mount and is regression-tested to never set
   `read_only: false`, `privileged: true`, or re-add capabilities.

### Tests (regression guards)

`tests/test_container_hardening.py` parses the Dockerfile and the two Compose files
and asserts each clause above. The guards are static (no Docker daemon required),
so they run on every CI machine and in pre-commit.

## Consequences

- **Positive** — Smaller attack surface (no `pip`/`wheel` in the runtime image, no
  capabilities, no privilege escalation, immutable rootfs); cleaner Docker Scout
  scans; OCI labels improve registry hygiene and SBOM correlation; regression tests
  block silent downgrades.
- **Trade-off** — Container patching with `pip install` inside a running image is
  no longer possible (intentional). Operators must rebuild the image. This matches
  the 12-factor "build, release, run" separation already documented in
  [`docs/DOCKER_SETUP.md`](../DOCKER_SETUP.md).
- **Compatibility** — Compose `read_only: true` requires that the application only
  writes under `/data` (volume) or `/tmp` (tmpfs). Data Boar already writes session
  SQLite, Excel reports, heatmaps, and audit logs under the configured `/data` path,
  so no code change is required.
- **Deferred** — Migration to a **Distroless** or **Wolfi** runtime base is **not**
  in this ADR. That swap interacts with `libpq5` / `libffi8` / `unixodbc` /
  `libmariadb3` runtime libraries and needs its own SBOM diff and Scout run; it is
  tracked as a follow-up slice. The current `python:3.13-slim` runtime stage is
  Scout-recommended at the time of writing and is a strict improvement over the
  prior posture.
- **Manifesto alignment** — Defensive Scanning Manifesto §1 ("no surprise side
  effects") is preserved: the database / connector code paths are untouched. The
  Art of the Fallback's monotonic-degradation rule is honoured: the override example
  cannot silently weaken the hardening contract because the regression tests refuse
  PRs that try.

## References

- [`Dockerfile`](../../Dockerfile)
- [`deploy/docker-compose.yml`](../../deploy/docker-compose.yml)
- [`deploy/docker-compose.override.example.yml`](../../deploy/docker-compose.override.example.yml)
- [`tests/test_container_hardening.py`](../../tests/test_container_hardening.py)
- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
- [`docs/DOCKER_SETUP.md`](../DOCKER_SETUP.md)
- [`docs/ops/DOCKER_IMAGE_RELEASE_ORDER.md`](../ops/DOCKER_IMAGE_RELEASE_ORDER.md)
