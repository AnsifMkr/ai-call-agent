import time
import logging
import sys
from src.core.exceptions import CircuitBreakerOpenError, ServiceUnavailableError, BaseResilienceError
from src.observability.logger import StructuredLogger, GoogleSheetsLogger, LogEntry
from src.observability.alerter import AlertManager, EmailChannel, TelegramChannel, WebhookChannel
from src.services.elevenlabs_service import ElevenLabsService
from src.services.llm_service import LLMService

# Configure basic logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MainSimulation")

def main():
    logger.info("Initializing AI Call Agent Resilience System...")

    # 1. Setup Observability
    structured_logger = StructuredLogger()
    sheets_logger = GoogleSheetsLogger()
    
    alert_manager = AlertManager()
    alert_manager.add_channel(EmailChannel("admin@system.com"))
    alert_manager.add_channel(TelegramChannel("-100123456789"))
    alert_manager.add_channel(WebhookChannel("https://webhook.site/xyz"))

    # 2. Setup Services
    eleven_labs = ElevenLabsService(alert_manager, structured_logger, sheets_logger)
    llm_service = LLMService(alert_manager, structured_logger, sheets_logger)

    contacts = ["User_A", "User_B", "User_C", "User_D", "User_E", "User_F", "User_G"]
    
    logger.info("Starting Call Processing Loop...")
    
    for i, contact in enumerate(contacts):
        logger.info(f"\n--- Processing Call for {contact} ---")
        
        # Scenario Automation:
        # After User_A (index 0), we trigger the outage.
        if i == 1: 
            logger.info("⚠️  INJECTING FAULT: Simulating ElevenLabs 503 Outage...")
            eleven_labs.simulate_503 = True
        
        # After User_D (index 3), we fix the outage.
        if i == 4:
            logger.info("✅  REMOVING FAULT: ElevenLabs Recovering...")
            eleven_labs.simulate_503 = False

        try:
            # 1. Get LLM Response
            response_text = llm_service.get_response(f"Hello {contact}")
            
            # 2. Generate Audio (Critical Path)
            try:
                audio = eleven_labs.generate_audio(response_text)
                logger.info(f"✅ Call Successful to {contact}")
            
            except CircuitBreakerOpenError:
                logger.warning(f"⛔ Circuit Breaker Open for ElevenLabs. Skipping {contact} (Graceful Degradation).")
                # Fallback Logic: Maybe send a distinct text or just log it
                structured_logger.log(LogEntry(
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    service_name="CallManager",
                    error_category="Fallback",
                    retry_count=0,
                    circuit_breaker_state="OPEN",
                    message=f"Skipped call to {contact} due to ElevenLabs CB Open"
                ))

            except BaseResilienceError as e:
                logger.error(f"❌ Call Failed to {contact} after retries: {e}")
        
        except Exception as e:
            logger.error(f"❌ Unexpected System Error for {contact}: {e}")

        # Simulate time passing between calls (so CB recovery timeout can tick)
        # We need to sleep enough to demonstrate CB recovery.
        # CB recovery is set to 15s in BaseService.
        # If we are at index 4 (recovery), we might need to wait for CB to try Half-Open.
        if i >= 1 and i <= 3:
            time.sleep(2) # Fast fail during outage
        else:
            time.sleep(5) # Normal pace

if __name__ == "__main__":
    main()
