# Import utility packages
import os
import joblib
from dotenv import load_dotenv

# Import bot
from src.core.bot import Telebot
from src.core.reccomender import Engine

# Import sklearn model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

if __name__ == "__main__":
    load_dotenv()

    # Load environment variables
    bot_token = os.getenv('BOT_TOKEN')
    api_token = os.getenv('API_TOKEN')

    # Load reccomender model and vectorizer
    vectorizer = joblib.load('./models/vectorizer.pkl')
    rev_map = joblib.load('./models/rev_map.pkl')
    matrix = joblib.load('./models/mov_matrix.pkl')

    # Instantiate reccomender engine class

    # Load telegram bot
    movie_bot = Telebot(bot_token)
    movie_bot.activate()