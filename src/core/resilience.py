import time
import functools
import logging
from .exceptions import TransientError, CircuitBreakerOpenError, BaseResilienceError

logger = logging.getLogger(__name__)

class RetryManager:
    def __init__(self, max_attempts=3, initial_delay=1.0, backoff_factor=2.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def execute(self, func, *args, **kwargs):
        """Executes the function with retry logic for TransientErrors."""
        attempt = 0
        delay = self.initial_delay
        last_exception = None

        while attempt < self.max_attempts:
            try:
                return func(*args, **kwargs)
            except TransientError as e:
                attempt += 1
                last_exception = e
                if attempt >= self.max_attempts:
                    logger.error(f"Retry limit reached ({self.max_attempts}) for {func.__name__}. Last error: {e}")
                    raise last_exception
                
                logger.warning(f"Transient error in {func.__name__}: {e}. Retrying in {delay}s (Attempt {attempt}/{self.max_attempts})")
                time.sleep(delay)
                delay *= self.backoff_factor
            except Exception as e:
                # Non-transient errors are re-raised immediately
                raise e
        
        if last_exception:
            raise last_exception

class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, service_name, failure_threshold=3, recovery_timeout=30):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs):
        """Executes the function if the circuit is allowed."""
        self._check_state()

        if self.state == CircuitBreakerState.OPEN:
            logger.warning(f"Circuit Breaker OPEN for {self.service_name}. Blocking call.")
            # Fail fast
            raise CircuitBreakerOpenError(f"Circuit Breaker is OPEN for {self.service_name}", service_name=self.service_name)

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except BaseResilienceError as e:
            # We track our custom resilience errors
            # Permanent errors might also trip the breaker depending on policy,
            # but usually CB is for availability/timeouts (Transient).
            # For this assignment, let's say ALL exceptions raised from the service wrapper 
            # (which might be wrapping everything in our custom exceptions) count towards failure 
            # if they indicate service health issues. 
            # However, typically 4xx (Permanent) shouldn't trip CB.
            if isinstance(e, TransientError):
                self._on_failure()
            raise e
        except Exception as e:
            # Unexpected errors also trip
            self._on_failure()
            raise e

    def _check_state(self):
        """Checks if enough time has passed to try HALF-OPEN."""
        if self.state == CircuitBreakerState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.recovery_timeout:
                logger.info(f"Circuit Breaker for {self.service_name} switching to HALF-OPEN.")
                self.state = CircuitBreakerState.HALF_OPEN

    def _on_success(self):
        """Resets failure count on success."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info(f"Circuit Breaker for {self.service_name} closed after successful probe.")
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Increments failure count and trips if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.error(f"Failure recorded for {self.service_name}. Count: {self.failure_count}/{self.failure_threshold}")

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.critical(f"Circuit Breaker for {self.service_name} RE-OPENED (Half-Open probe failed).")
        
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.critical(f"Circuit Breaker for {self.service_name} OPENED.")

