from dataclasses import dataclass

@dataclass
class RawCommiterData:
    github_login: str
    commits: int = 0
    closed_issues: int = 0