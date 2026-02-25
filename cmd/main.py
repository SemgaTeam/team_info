from dotenv import load_dotenv
import os
import internal.core as core
import internal.db as db

load_dotenv()

GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))
GITHUB_ORG = str(os.getenv("GITHUB_ORG"))
GITHUB_SECRET_TOKEN = str(os.getenv("GITHUB_SECRET_TOKEN"))

TELEGRAM_TOKEN = str(os.getenv("TELEGRAM_TOKEN"))
DB_PATH = "team.sqlite"

db = db.DB(DB_PATH)
db.init_db()

core = core.Core(db, GITHUB_TOKEN, GITHUB_ORG, GITHUB_SECRET_TOKEN)