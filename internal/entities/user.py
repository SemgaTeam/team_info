from dataclasses import dataclass

@dataclass
class User:
    id: int
    github_login: str
    telegram_id: str