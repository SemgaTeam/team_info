from dataclasses import dataclass

@dataclass
class BotWebhookEvent:
    github_login: str
    rating: int