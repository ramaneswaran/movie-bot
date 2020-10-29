# Import utility packages
import os
import pickle
from dotenv import load_dotenv

# Import bot
from src.core.bot import Telebot
from src.core.reccomender import Engine

# Import sklearn model
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Import spacy
import spacy

# Import ML libraries
import pandas as pd
import numpy as np

if __name__ == "__main__":
    load_dotenv()

    # Load environment variables
    bot_token = os.getenv('BOT_TOKEN')
    api_token = os.getenv('API_TOKEN')

    # Load reccomender model and vectorizer
    vectorizer = pickle.load(open('./models/pkl_vec.pkl', 'rb'))
    matrix = pickle.load(open('./models/database.pkl', 'rb'))
    rev_map = pickle.load(open('./models/id2imdb.pkl', 'rb'))

    metadata = pd.read_csv('./data/metadata.csv')
       

    # Instantiate reccomender engine class
    engine = Engine(vectorizer, matrix, rev_map, metadata)

    # Load spacy model
    nlp = spacy.load('./models/ner')

    # Load telegram bot
    movie_bot = Telebot(bot_token, api_token, engine, nlp)
    movie_bot.activate()