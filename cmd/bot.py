from .main import core, TELEGRAM_TOKEN
from internal.bot import Bot

bot = Bot(TELEGRAM_TOKEN, core)
bot.run()