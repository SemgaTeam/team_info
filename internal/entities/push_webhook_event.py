from dataclasses import dataclass
from typing import List

@dataclass
class PushWebhookEvent:
    commits: List[Commit]

@dataclass
class Commit:
    author: Author

@dataclass
class Author:
    name: str
    username: str