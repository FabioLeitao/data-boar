"""
Scan session identification: UUID v4 + timestamp.
Used for log correlation and API routes (/list, /reports/{session_id}).
"""
import uuid
from datetime import datetime


def new_session_id() -> str:
    """Return a unique session id: UUID4 and ISO timestamp."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    u = uuid.uuid4().hex[:12]
    return f"{u}_{ts}"
