import logging

logger = logging.getLogger(__name__)

class AlertChannel:
    def send(self, message: str):
        raise NotImplementedError

class EmailChannel(AlertChannel):
    def __init__(self, recipient_email):
        self.recipient_email = recipient_email

    def send(self, message: str):
        # Simulation of sending email
        logger.warning(f"📧 [EMAIL ALERT] To: {self.recipient_email} | Body: {message}")
        print(f"📧 [EMAIL SENT] {message}")

class TelegramChannel(AlertChannel):
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def send(self, message: str):
        # Simulation of sending telegram msg
        logger.warning(f"📱 [TELEGRAM ALERT] ChatID: {self.chat_id} | Msg: {message}")
        print(f"📱 [TELEGRAM SENT] {message}")

class WebhookChannel(AlertChannel):
    def __init__(self, url):
        self.url = url

    def send(self, message: str):
        # Simulation of sending webhook
        logger.warning(f"🔗 [WEBHOOK ALERT] URL: {self.url} | Payload: {message}")
        print(f"🔗 [WEBHOOK SENT] {message}")

class AlertManager:
    def __init__(self):
        self.channels = []

    def add_channel(self, channel: AlertChannel):
        self.channels.append(channel)

    def alert(self, subject: str, body: str):
        full_message = f"[{subject}] {body}"
        for channel in self.channels:
            try:
                channel.send(full_message)
            except Exception as e:
                logger.error(f"Failed to alert channel {channel}: {e}")
