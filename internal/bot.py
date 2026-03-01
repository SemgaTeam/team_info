import re

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from .core import get_league_name
from .core import Core

from .entities import MemberStats, User, ChangeUserRatingEvent

from typing import List, Dict

class Bot:
    def __init__(self, telegram_token: str, core: Core):
        app = ApplicationBuilder().token(telegram_token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("leaderboard", self.leaderboard))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

        self.users: Dict[str, str] = {} # github_login:chat_id
        self.pending_github_login_chats: set[str] = set()
        self.TELEGRAM_TOKEN = telegram_token
        self.app = app
        self.core = core
    
    def run(self):
        print("Бот запущен...")
        self.app.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else None
        if chat_id is None:
            return

        chat_id_str = str(chat_id)
        self.pending_github_login_chats.add(chat_id_str)

        await update.message.reply_text( # pyright: ignore[reportOptionalMemberAccess]
            "Привет! Введи свой GitHub login:"
        )


    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else None
        message_text = update.message.text if update.message else None
        if chat_id is None or message_text is None:
            return

        chat_id_str = str(chat_id)
        if chat_id_str not in self.pending_github_login_chats:
            return

        github_login = message_text.strip()
        if not self.is_valid_github_login(github_login):
            await update.message.reply_text( # pyright: ignore[reportOptionalMemberAccess]
                "Некорректный GitHub login. Используй только буквы, цифры и '-', от 1 до 39 символов."
            )
            return

        self.users[github_login] = chat_id_str
        self.pending_github_login_chats.remove(chat_id_str)

        await update.message.reply_text(f"Сохранил login: {github_login}") # pyright: ignore[reportOptionalMemberAccess]


    def is_valid_github_login(self, github_login: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", github_login))


    async def change_user_rating(self, event: ChangeUserRatingEvent):
        chat_id = self.users[event.github_login]
        if chat_id is None:
            return
        
        await self.app.bot.send_message(chat_id, "Заработан рейтинг: +" + str(event.rating))


    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        loading_message = await update.message.reply_text("Собираем данные, это может занять несколько секунд... ⏳") # pyright: ignore[reportOptionalMemberAccess]

        stats = await self.core.load_stats()

        msg = format_leaderboard(stats)

        await loading_message.edit_text(msg)
    

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
