"""Licensing errors raised when enforcement blocks a scan."""


class LicenseBlockedError(RuntimeError):
    """Raised when licensing enforcement blocks starting an audit or digest session."""

    def __init__(self, state: str, message: str) -> None:
        self.state = state
        super().__init__(message)
