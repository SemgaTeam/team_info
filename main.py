import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

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

# --- Асинхронные функции для GitHub ---
async def fetch_json(session, url, params=None):
    async with session.get(url, headers=HEADERS, params=params) as resp:
        if resp.status != 200:
            return []
        return await resp.json()

async def get_org_members(session, org_name):
    members = []
    page = 1
    while True:
        data = await fetch_json(session, f"https://api.github.com/orgs/{org_name}/members", {"per_page": 100, "page": page})
        if not data:
            break
        members.extend([m["login"] for m in data])
        page += 1
    return members

async def get_org_repos(session, org_name):
    repos = []
    page = 1
    while True:
        data = await fetch_json(session, f"https://api.github.com/orgs/{org_name}/repos", {"per_page": 100, "page": page})
        if not data:
            break
        repos.extend([r["name"] for r in data])
        page += 1
    return repos

async def get_member_stats(session, org_name, member, repos):
    commits = 0
    closed_issues = 0

    async def fetch_commits(repo):
        count = 0
        page = 1
        while True:
            data = await fetch_json(session, f"https://api.github.com/repos/{org_name}/{repo}/commits",
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

# --- Команда /leaderboard ---
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loading_message = await update.message.reply_text("Собираем данные, это может занять несколько секунд... ⏳")
    async with aiohttp.ClientSession() as session:
        members = await get_org_members(session, GITHUB_ORG)
        repos = await get_org_repos(session, GITHUB_ORG)

        tasks = [get_member_stats(session, GITHUB_ORG, member, repos) for member in members]
        results = await asyncio.gather(*tasks)

        leaderboard_data = []
        for member, (commits, issues) in zip(members, results):
            score = commits + issues
            leaderboard_data.append((member, commits, issues, score))

        leaderboard_data.sort(key=lambda x: x[3], reverse=True)

        msg = "🏆 Лидерборд команды:\n\n"
        for i, (member, commits, issues, score) in enumerate(leaderboard_data, start=1):
            league = get_league_name(score)
            msg += (
                f"{i}. {member}: {score} | {league} "
                f"(Коммиты: {commits}, Закрытые Issues: {issues})\n"
            )

        await loading_message.edit_text(msg)

# --- Запуск бота ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    print("Бот запущен...")
    app.run_polling()
