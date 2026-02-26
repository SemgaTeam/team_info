from dataclasses import dataclass

@dataclass
class BotWebhookEvent:
    login: str
    rating: int