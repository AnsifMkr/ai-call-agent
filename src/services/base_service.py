import time
import logging
from src.core.resilience import RetryManager, CircuitBreaker
from src.observability.logger import LogEntry
from src.core.exceptions import BaseResilienceError

logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self, service_name, alert_manager, structured_logger, sheets_logger):
        self.service_name = service_name
        self.alert_manager = alert_manager
        self.structured_logger = structured_logger
        self.sheets_logger = sheets_logger
        
        # Resilience Primitives
        self.retry_manager = RetryManager(max_attempts=3, initial_delay=1.0) # Configurable
        self.circuit_breaker = CircuitBreaker(service_name=service_name, failure_threshold=3, recovery_timeout=15)

        self.last_health_status = True

    def check_health(self):
        """Standard health check mechanism."""
        # Simple check based on Circuit Breaker state
        # In a real scenario, this might hit a /status endpoint
        is_circuit_open = (self.circuit_breaker.state == "OPEN")
        self.last_health_status = not is_circuit_open
        return self.last_health_status

    def log_event(self, category, message, error=None):
        """Unified logging helper."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = LogEntry(
            timestamp=timestamp,
            service_name=self.service_name,
            error_category=category,
            retry_count=self.circuit_breaker.failure_count, # Approximate metric
            circuit_breaker_state=self.circuit_breaker.state,
            message=message
        )
        self.structured_logger.log(entry)
        self.sheets_logger.log(entry)

        if error:
            logger.error(f"[{self.service_name}] {message} | Error: {error}")

    def execute_with_resilience(self, func, *args, **kwargs):
        """Wraps execution with Circuit Breaker and Retry logic."""
        def wrapped_operation():
            return func(*args, **kwargs)
        
        # We wrap the operation in the retry manager, 
        # AND that entire block is guarded by the circuit breaker.
        # Order: Circuit Breaker -> Retry -> Function
        # This means if CB is open, we don't retry.
        # If CB is closed, we try, and if transient error, we retry inside.
        
        try:
            return self.circuit_breaker.call(
                self.retry_manager.execute, 
                wrapped_operation
            )
        except Exception as e:
            # Check if we need to alert
            if self.circuit_breaker.state == "OPEN":
                self.alert_manager.alert(
                    subject=f"CRITICAL: {self.service_name} Circuit Open",
                    body=f"Circuit breaker opened due to repeated failures. Last error: {e}"
                )
            
            self.log_event("FAILURE", f"Operation failed: {str(e)}", error=e)
            raise e
