import os
import asyncio
from dotenv import load_dotenv
import uvicorn

import internal.core as core
import internal.db as db
from internal.event_bus import EventBus
from internal.server import get_app
from internal.bot import Bot
from internal.entities import ChangeUserRatingEvent

load_dotenv()

GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))
GITHUB_ORG = str(os.getenv("GITHUB_ORG"))
GITHUB_SECRET_TOKEN = str(os.getenv("GITHUB_SECRET_TOKEN"))

TELEGRAM_TOKEN = str(os.getenv("TELEGRAM_TOKEN"))
DB_PATH = "team.sqlite"

db = db.DB(DB_PATH)
db.init_db()

core = core.Core(db, GITHUB_TOKEN, GITHUB_ORG, GITHUB_SECRET_TOKEN)
event_bus = EventBus()

app = get_app(lambda: core, lambda: event_bus)

bot = Bot(TELEGRAM_TOKEN, core)
event_bus.subscribe(ChangeUserRatingEvent, bot.change_user_rating)

async def main():
    await bot.run()

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8080,
        loop="asyncio",
        reload=False
    )

    server = uvicorn.Server(config)
    await server.serve()
    await bot.app.stop()
    await bot.app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())