import logging
import random
from src.services.base_service import BaseService
from src.core.exceptions import ServiceUnavailableError, AuthError

logger = logging.getLogger(__name__)

class ElevenLabsService(BaseService):
    def __init__(self, alert_manager, structured_logger, sheets_logger):
        super().__init__("ElevenLabs", alert_manager, structured_logger, sheets_logger)
        self.simulate_503 = False # Flag to trigger simulation scenario

    def generate_audio(self, text):
        return self.execute_with_resilience(self._generate_audio_impl, text)

    def _generate_audio_impl(self, text):
        logger.info(f"ElevenLabs requesting audio for: '{text[:20]}...'")
        
        if self.simulate_503:
            logger.warning("Simulating ElevenLabs 503 Service Unavailable")
            raise ServiceUnavailableError("ElevenLabs API is returning 503", service_name="ElevenLabs")

        # Simulate chance of random other transient error if needed, 
        # but for this assignment we control it via the flag mainly.
        
        return f"Audio_Bytes_For_[{text[:10]}]"
