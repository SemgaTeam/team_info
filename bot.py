import os

import asyncio
import aiohttp

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from core import *

class Bot:
    def __init__(self, telegram_token: str, github_org: str):
        app = ApplicationBuilder().token(telegram_token).build()
        app.add_handler(CommandHandler("leaderboard", self.leaderboard))

        self.TELEGRAM_TOKEN = telegram_token
        self.GITHUB_ORG = github_org
        self.app = app
    
    def run(self):
        print("Бот запущен...")
        self.app.run_polling()


    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        loading_message = await update.message.reply_text("Собираем данные, это может занять несколько секунд... ⏳")
        async with aiohttp.ClientSession() as session:
            members = await get_org_members(session, self.GITHUB_ORG)
            repos = await get_org_repos(session, self.GITHUB_ORG)

            tasks = [get_member_stats(session, self.GITHUB_ORG, member, repos) for member in members]
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