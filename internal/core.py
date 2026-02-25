import asyncio
import json
from typing import Any, List
import aiohttp
from dotenv import load_dotenv

from .db import DB
from .utils import *

load_dotenv()

class Core:
    def __init__(self, db: DB, GITHUB_TOKEN: str, GITHUB_ORG: str):
        self.db = db
        self.GITHUB_TOKEN = GITHUB_TOKEN
        self.GITHUB_ORG = GITHUB_ORG

    async def get_members_stats(self) -> List[Any]:
        return self.db.get_members_stats()

    async def backfill(self, org_name: str | None = None) -> None:
        target_org = org_name or self.GITHUB_ORG
        if not target_org:
            raise ValueError("GITHUB_ORG is not set")

        async with aiohttp.ClientSession() as session:
            members = await get_org_members(session, target_org, self.GITHUB_TOKEN)
            repos = await get_org_repos(session, target_org, self.GITHUB_TOKEN)
            stats = await asyncio.gather(
                *(get_member_stats(session, target_org, member, repos, self.GITHUB_TOKEN) for member in members)
            )

        now = utc_now_iso()
        for member, (commits, issues) in zip(members, stats):
            self.db.insert_member_stats(member, commits, issues, now)

    async def handle_webhook_event(self, event_type, sender_login, repository_name, payload, received_at):
        payload_json = json.dumps(payload, ensure_ascii=False)

        self.db.insert_webhook_event(event_type, sender_login, repository_name, payload_json, received_at)

        if event_type == "push":
            self.handle_push_event(payload)
        elif event_type == "issues":
            self.handle_issues_event(payload)

    def upsert_member_commits(self, login: str, amount: int) -> None:
        commits = 0
        issues = 0
        stats = self.db.get_member_stats_by_login(login)
        if stats:
            commits, issues, _ = stats

        now = utc_now_iso()

        self.db.insert_member_stats(login, commits+amount, issues, now) # pyright: ignore[reportPossiblyUnboundVariable]


    def upsert_member_closed_issue(self, login: str) -> None:
        commits = 0
        issues = 0
        stats = self.db.get_member_stats_by_login(login)
        if stats:
            commits, issues, _ = stats

        now = utc_now_iso()
        self.db.insert_member_stats(login, commits, issues+1, now)


    def handle_push_event(self, payload: dict) -> None:
        commits = payload.get("commits", [])
        authors_count: dict[str, int] = {}
        for commit in commits:
            author = commit.get("author") or {}
            login = author.get("username")
            if not login:
                continue
            authors_count[login] = authors_count.get(login, 0) + 1

        # Fallback for squash/empty details: attribute all commits to sender.
        if not authors_count and commits:
            sender = (payload.get("sender") or {}).get("login")
            if sender:
                authors_count[sender] = len(commits)

        for login, amount in authors_count.items():
            self.upsert_member_commits(login, amount)


    def handle_issues_event(self, payload: dict) -> None:
        if payload.get("action") != "closed":
            return
        issue = payload.get("issue") or {}
        creator = issue.get("user") or {}
        login = creator.get("login")
        if login:
            self.upsert_member_closed_issue(login)

def get_league_name(score: int) -> str:
    if score >= 120:
        return "Лига Ctrl+C / Ctrl+V Магистров"
    if score >= 80:
        return "Лига Ночных Деплоев"
    if score >= 50:
        return "Лига Почти Без Багов"
    if score >= 20:
        return "Лига Сломал-Починил"
    return "Лига Первого Коммита"