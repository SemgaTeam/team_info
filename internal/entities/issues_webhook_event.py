from dataclasses import dataclass
from .user import User

@dataclass
class IssuesWebhookEvent:
    action: str
    sender: User
    issue: Issue

@dataclass
class Issue:
    repository_url: str