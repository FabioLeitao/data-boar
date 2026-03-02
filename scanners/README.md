# scanners/ – Legacy

**Prefer:** `main.py` + `core.engine` + `connectors.sql_connector` / `connectors.filesystem_connector` for all scanning.

This folder contains legacy scanner code that may reference missing modules (`src.*`). New code should use the unified flow in `core/` and `connectors/`.
