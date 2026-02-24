from dotenv import load_dotenv
import os
import bot
import core
import db
from server import get_app

load_dotenv()

GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))
GITHUB_ORG = str(os.getenv("GITHUB_ORG"))
TELEGRAM_TOKEN = str(os.getenv("TELEGRAM_TOKEN"))
DB_PATH = "team.sqlite"

db = db.DB(DB_PATH)
db.init_db()

core = core.Core(db, GITHUB_TOKEN, GITHUB_ORG)

bot = bot.Bot(TELEGRAM_TOKEN, core)

app = get_app(lambda: core)