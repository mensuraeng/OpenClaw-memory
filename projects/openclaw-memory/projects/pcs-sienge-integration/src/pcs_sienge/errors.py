class SiengeIntegrationError(Exception):
    """Base error for PCS ↔ Sienge integration."""


class SiengeConfigError(SiengeIntegrationError):
    """Configuration error."""


class SiengeAuthError(SiengeIntegrationError):
    """Authentication error."""


class SiengeApiError(SiengeIntegrationError):
    """HTTP/API error."""

    def __init__(self, status_code: int, message: str, payload: str | None = None):
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"[{status_code}] {message}")
