from dataclasses import dataclass

@dataclass
class ChangeUserRatingEvent:
    github_login: str
    rating: int