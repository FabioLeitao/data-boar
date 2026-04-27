"""Regression guards for Data Boar container image hardening.

These guards encode the decisions in
[`docs/adr/0044-container-image-hardening-databoar-user.md`](../docs/adr/0044-container-image-hardening-databoar-user.md):

- Multi-stage build (builder + minimal runtime) keeps gcc / -dev out of the final image.
- Final image runs as the dedicated non-root `databoar` user (uid 1000).
- Pip / wheel are removed from the runtime stage so Docker Scout has nothing to flag.
- HEALTHCHECK is declared in the image so plain `docker run` surfaces liveness.
- Compose stack pins read_only, cap_drop ALL, no-new-privileges, and a tmpfs at /tmp.

The guards are static (text + YAML inspection); they do NOT spin up Docker. CI machines
without the daemon still run them. They exist to prevent silent posture regressions when
someone refactors the Dockerfile or compose files — same intent as
`tests/test_about_version_matches_pyproject.py` for the version surface.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = REPO_ROOT / "Dockerfile"
COMPOSE_FILE = REPO_ROOT / "deploy" / "docker-compose.yml"
COMPOSE_OVERRIDE_EXAMPLE = REPO_ROOT / "deploy" / "docker-compose.override.example.yml"


def _read_dockerfile() -> str:
    assert DOCKERFILE.is_file(), f"missing Dockerfile: {DOCKERFILE}"
    return DOCKERFILE.read_text(encoding="utf-8")


def _load_compose(path: Path) -> dict:
    assert path.is_file(), f"missing compose file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path.name} must parse to a mapping"
    return data


# --------------------------------------------------------------------------- #
# Dockerfile guards
# --------------------------------------------------------------------------- #


def test_dockerfile_uses_multistage_build() -> None:
    text = _read_dockerfile()
    # Builder stage tag + final FROM without `AS`.
    assert "FROM python:3.13-slim AS builder" in text, (
        "Dockerfile must declare a `builder` stage so build tools never reach the runtime image."
    )
    # At least two FROM lines — one tagged `builder`, one final unnamed runtime stage.
    from_lines = [line for line in text.splitlines() if line.startswith("FROM ")]
    assert len(from_lines) >= 2, "Dockerfile must be multi-stage (>= 2 FROM lines)."


def test_dockerfile_runtime_runs_as_databoar_non_root() -> None:
    text = _read_dockerfile()
    assert "useradd -r -u 1000 -g 1000 -d /data -s /sbin/nologin databoar" in text, (
        "Dockerfile must create the dedicated non-root `databoar` user (uid 1000, /sbin/nologin)."
    )
    assert "USER databoar" in text, (
        "Dockerfile must drop privileges with `USER databoar` before CMD."
    )
    # No `USER root` after we drop to databoar — that would silently re-elevate.
    after_user_drop = text.split("USER databoar", 1)[1]
    assert "USER root" not in after_user_drop, (
        "Dockerfile must not switch back to `USER root` after dropping privileges."
    )


def test_dockerfile_runtime_has_no_build_tools() -> None:
    """Final stage must not `apt-get install` gcc / build-essential / -dev packages.

    The first apt block belongs to the builder stage; the second (after the second
    FROM) is the runtime — it may install runtime libs only (libpq5, libffi8, ...).

    Inspect the *executable* RUN lines only, not the surrounding comment prose,
    so that documenting "this stage must not install -dev" does not accidentally
    fail the guard.
    """
    text = _read_dockerfile()
    runtime_start = text.find("FROM python:3.13-slim\n")
    assert runtime_start != -1, "expected unnamed final FROM in Dockerfile"
    runtime_section = text[runtime_start:]

    forbidden_runtime_pkgs = ("build-essential", "gcc", "g++", "pkg-config", "-dev")
    for raw_line in runtime_section.splitlines():
        # Skip pure comments and blank lines — only RUN / shell continuations matter.
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # apt-get install lines (and their `\` continuations) are what we audit.
        # Heuristic: any executable line in the runtime section that mentions
        # `apt-get install` or continues an install block.
        if "apt-get install" not in stripped and not stripped.endswith("\\"):
            continue
        for token in forbidden_runtime_pkgs:
            assert token not in stripped, (
                f"runtime stage must not install build tooling: found `{token}` "
                f"in line `{stripped}` after the final FROM."
            )


def test_dockerfile_runtime_drops_pip_and_wheel() -> None:
    """Pip and wheel are removed from the runtime image (attack surface reduction).

    Keeping them only re-introduces Docker Scout CVE noise on every refresh; deps
    are already installed in the builder stage and copied via site-packages.
    """
    text = _read_dockerfile()
    runtime_start = text.find("FROM python:3.13-slim\n")
    assert runtime_start != -1
    runtime_section = text[runtime_start:]
    assert "rm -f /usr/local/bin/pip" in runtime_section, (
        "runtime stage must remove the `pip` binaries (attack-surface reduction)."
    )
    assert "/usr/local/bin/wheel" in runtime_section, (
        "runtime stage must remove the `wheel` binary alongside pip."
    )


def test_dockerfile_declares_healthcheck() -> None:
    text = _read_dockerfile()
    assert "HEALTHCHECK" in text, (
        "Dockerfile must declare HEALTHCHECK so `docker run` (no Compose) shows liveness."
    )
    assert "/health" in text, "HEALTHCHECK must hit the /health endpoint."


def test_dockerfile_declares_oci_labels() -> None:
    text = _read_dockerfile()
    required_labels = (
        "org.opencontainers.image.title",
        "org.opencontainers.image.source",
        "org.opencontainers.image.licenses",
        "org.opencontainers.image.version",
    )
    for label in required_labels:
        assert label in text, f"Dockerfile must declare OCI label `{label}`."


# --------------------------------------------------------------------------- #
# docker-compose.yml hardening posture
# --------------------------------------------------------------------------- #


def _data_boar_service(compose: dict) -> dict:
    services = compose.get("services") or {}
    assert "lgpd-audit" in services, "compose file must define the `lgpd-audit` service"
    svc = services["lgpd-audit"]
    assert isinstance(svc, dict), "service definition must be a mapping"
    return svc


def test_compose_pins_non_root_user() -> None:
    svc = _data_boar_service(_load_compose(COMPOSE_FILE))
    assert str(svc.get("user")) == "1000:1000", (
        'compose must pin `user: "1000:1000"` so Swarm / k8s cannot re-root the process.'
    )


def test_compose_filesystem_is_read_only() -> None:
    svc = _data_boar_service(_load_compose(COMPOSE_FILE))
    assert svc.get("read_only") is True, (
        "compose must set `read_only: true` for the audit container."
    )
    tmpfs = svc.get("tmpfs") or []
    assert any("/tmp" in entry for entry in tmpfs), (
        "compose must mount a tmpfs at /tmp when read_only is enabled."
    )


def test_compose_drops_all_capabilities_and_blocks_priv_escalation() -> None:
    svc = _data_boar_service(_load_compose(COMPOSE_FILE))
    cap_drop = svc.get("cap_drop") or []
    assert "ALL" in cap_drop, "compose must drop ALL capabilities (`cap_drop: [ALL]`)."
    assert not (svc.get("cap_add") or []), (
        "compose must not add capabilities back unless an ADR explicitly justifies it."
    )
    sec_opt = svc.get("security_opt") or []
    assert "no-new-privileges:true" in sec_opt, (
        "compose must set `security_opt: [no-new-privileges:true]`."
    )


def test_compose_caps_pids_and_open_files() -> None:
    svc = _data_boar_service(_load_compose(COMPOSE_FILE))
    assert isinstance(svc.get("pids_limit"), int) and svc["pids_limit"] > 0, (
        "compose must set a positive integer `pids_limit` for runaway protection."
    )
    nofile = (svc.get("ulimits") or {}).get("nofile") or {}
    assert nofile.get("soft") and nofile.get("hard"), (
        "compose must set `ulimits.nofile` (soft + hard) for the audit container."
    )


# --------------------------------------------------------------------------- #
# Override example must not weaken the hardening posture
# --------------------------------------------------------------------------- #


def test_override_example_does_not_weaken_hardening() -> None:
    data = _load_compose(COMPOSE_OVERRIDE_EXAMPLE)
    services = data.get("services") or {}
    svc = services.get("lgpd-audit") or {}
    forbidden_downgrades = {
        "read_only": False,
        "privileged": True,
    }
    for key, bad_value in forbidden_downgrades.items():
        if key in svc:
            assert svc[key] != bad_value, (
                f"override example must not set `{key}: {bad_value}` "
                "(would silently weaken the hardening contract)."
            )
    # cap_add reintroducing capabilities is a posture downgrade by definition.
    assert not svc.get("cap_add"), (
        "override example must not re-add Linux capabilities; use a dedicated dev "
        "compose file instead so the example stays safe-by-default."
    )
