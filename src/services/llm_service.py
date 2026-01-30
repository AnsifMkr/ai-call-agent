import logging
from src.services.base_service import BaseService
from src.core.exceptions import NetworkTimeoutError, QuotaExceededError

logger = logging.getLogger(__name__)

class LLMService(BaseService):
    def __init__(self, alert_manager, structured_logger, sheets_logger):
        super().__init__("LLM_Provider", alert_manager, structured_logger, sheets_logger)
        self.simulate_timeout = False

    def get_response(self, prompt):
        return self.execute_with_resilience(self._get_response_impl, prompt)

    def _get_response_impl(self, prompt):
        logger.info(f"LLM generating response for: '{prompt[:20]}...'")

        if self.simulate_timeout:
            logger.warning("Simulating LLM Network Timeout")
            raise NetworkTimeoutError("LLM API Timed out", service_name="LLM_Provider")

        return f"LLM_Response_For_[{prompt[:10]}]"
