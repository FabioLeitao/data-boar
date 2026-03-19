-- Local audit DB for issuance events (run with sqlite3: sqlite3 audit.sqlite < schema/audit.sql)
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
