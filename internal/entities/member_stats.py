from dataclasses import dataclass

@dataclass
class MemberStats:
    user_id: int
    commits: int
    closed_issues: int
    updated_at: str
