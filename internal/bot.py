from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from .core import get_league_name
from .core import Core

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

        stats = await self.core.get_members_stats()

        if not stats:
            await loading_message.edit_text(
                "🏆 Лидерборд команды:\n\nПока нет данных. "
            )
            return

        msg = "🏆 Лидерборд команды:\n\n"
        for i, stat in enumerate(stats, start=1):
            score = stat.commits + stat.closed_issues
            league = get_league_name(score)

            user = await self.core.get_user_by_id(stat.user_id)

            msg += (
                f"{i}. {user.github_login}: {score} | {league} "
                f"(Коммиты: {stat.commits}, Закрытые Issues: {stat.closed_issues})\n"
            )

        await loading_message.edit_text(msg)