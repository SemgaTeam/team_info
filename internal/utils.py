import asyncio

from datetime import datetime, timezone
async def fetch_json(session, url, github_token, params=None):
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    async with session.get(url, headers=headers, params=params) as resp:
        if resp.status != 200:
            return []
        return await resp.json()

async def get_org_members(session, org_name, github_token):
    members = []
    page = 1
    while True:
        data = await fetch_json(session, f"https://api.github.com/orgs/{org_name}/members", github_token, {"per_page": 100, "page": page})
        if not data:
            break
        members.extend([m["login"] for m in data])
        page += 1
    return members

async def get_org_repos(session, org_name, github_token):
    repos = []
    page = 1
    while True:
        data = await fetch_json(session, f"https://api.github.com/orgs/{org_name}/repos", github_token, {"per_page": 100, "page": page})
        if not data:
            break
        repos.extend([r["name"] for r in data])
        page += 1
    return repos

async def get_member_stats(session, org_name, member, repos, github_token):
    commits = 0
    closed_issues = 0

    async def fetch_commits(repo):
        count = 0
        page = 1
        while True:
            data = await fetch_json(session, f"https://api.github.com/repos/{org_name}/{repo}/commits", 
                                    github_token,
                                    {"author": member, "per_page": 100, "page": page})
            if not data:
                break
            count += len(data)
            page += 1
        return count

    async def fetch_issues(repo):
        count = 0
        page = 1
        while True:
            data = await fetch_json(session, f"https://api.github.com/repos/{org_name}/{repo}/issues",
                                    github_token,
                                    {"state": "closed", "creator": member, "per_page": 100, "page": page})
            if not data:
                break
            count += len(data)
            page += 1
        return count

    # Запускаем для всех репозиториев параллельно
    commits_list = await asyncio.gather(*(fetch_commits(repo) for repo in repos))
    issues_list = await asyncio.gather(*(fetch_issues(repo) for repo in repos))

    commits = sum(commits_list)
    closed_issues = sum(issues_list)
    return commits, closed_issues

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()