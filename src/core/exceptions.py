class BaseResilienceError(Exception):
    """Base class for all resilience-related errors."""
    def __init__(self, message, service_name=None):
        super().__init__(message)
        self.service_name = service_name
        self.message = message

class TransientError(BaseResilienceError):
    """Errors that are temporary and can be retried (e.g., 503, Timeout)."""
    pass

class PermanentError(BaseResilienceError):
    """Errors that are permanent and should not be retried (e.g., 401, 400)."""
    pass

class ServiceUnavailableError(TransientError):
    """Specific error for 503 Service Unavailable."""
    pass

class NetworkTimeoutError(TransientError):
    """Specific error for network timeouts."""
    pass

class AuthError(PermanentError):
    """Specific error for authentication failures."""
    pass

class QuotaExceededError(PermanentError):
    """Specific error for quota limits."""
    pass

class CircuitBreakerOpenError(BaseResilienceError):
    """Raised when execution is blocked by an open circuit breaker."""
    pass
