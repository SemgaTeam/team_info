from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from .core import get_league_name
from .core import Core

from entities import MemberStats, User

from typing import List 

class Bot:
    def __init__(self, telegram_token: str, core: Core):
        app = ApplicationBuilder().token(telegram_token).build()
        app.add_handler(CommandHandler("leaderboard", self.leaderboard))

        self.TELEGRAM_TOKEN = telegram_token
        self.app = app
        self.core = core
    
    def run(self):
        print("Бот запущен...")
        self.app.run_polling()


    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        loading_message = await update.message.reply_text("Собираем данные, это может занять несколько секунд... ⏳") # pyright: ignore[reportOptionalMemberAccess]

        stats = await self.load_stats()

        msg = format_leaderboard(stats)

        await loading_message.edit_text(msg)

    
    async def load_stats(self) -> List[tuple[MemberStats, User, int]]:
        stats = await self.core.get_members_stats()

        users: List[User] = []
        rating: List[int] = []
        for stat in stats:
            user = await self.core.get_user_by_id(stat.user_id)
            users.append(user)

            user_rating = self.core.calculate_rating(stat)
            rating.append(user_rating)

        return list(zip(
            stats,
            users,
            rating
        ))
        

def format_leaderboard(stats: List[tuple[MemberStats, User, int]]) -> str:
    if not stats:
        return "🏆 Лидерборд команды:\n\nПока нет данных. "

    msg = "🏆 Лидерборд команды:\n\n"
    for i, (stat, user, rating) in enumerate(stats, start=1):
        league = get_league_name(rating)

        msg += (
            f"{i}. {user.github_login}: {rating} | {league} "
            f"(Коммиты: {stat.commits}, Закрытые Issues: {stat.closed_issues})\n"
        )

    return msg