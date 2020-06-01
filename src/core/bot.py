import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

# Import utility functions for API
from src.utils.api_utilities import get_meta_data, get_movie_detail, get_rating
from src.utils.api_utilities import get_plot


class Telebot:
    def __init__(self, bot_token, api_token, engine, nlp):

        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.engine = engine

        self.nlp = nlp

        self.api_token = api_token

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='I am a bot')
    


    def echo(self, update, context):
        
        plot = ""
        try:
            movie_title = self.get_movie_title(update.message.text)

            if movie_title == -1:
                raise Exception("Movie title could not be extracted")

            plot = get_plot(movie_title, self.api_token)

            if plot == -1:
                raise Exception("Movie not found in OMDB")
            
        except Exception as error:
            print(error)

        
        context.bot.send_message(chat_id=update.effective_chat.id, text=plot)
    
    def get_movie_title(self, text):
        '''
        This function extracts and returns movie name
        '''
        print(text)
        doc = self.nlp(text)

        movie_title = ""
        try:
            
            movie_title = doc.ents[0].text

        except Exception as error:
            return -1

        return movie_title

    def register_handlers(self):
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(Filters.text, self.echo)
        
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(echo_handler)

    def activate(self):
        self.register_handlers()
        self.updater.start_polling()
