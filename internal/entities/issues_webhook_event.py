from dataclasses import dataclass
@dataclass
class IssuesWebhookEvent:
    action: str
    sender: User
    issue: Issue

@dataclass
class Issue:
    repository_url: str

@dataclass
class User:
    login: str