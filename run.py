import os
from dotenv import load_dotenv

# Import bot
from src.core.bot import Telebot
from src.core.reccomender import Engine

if __name__ == "__main__":
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    movie_bot = Telebot(bot_token)
    movie_bot.activate()