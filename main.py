from dotenv import load_dotenv
import os
import bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")

if __name__ == "__main__":
    bot = bot.Bot(TELEGRAM_TOKEN, GITHUB_ORG)
    bot.run()