import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

# Import utility functions for API
from src.utils.api_utils import get_metadata, get_movie_detail, get_rating
from src.utils.api_utils import get_plot
from src.utils.bot_utils import build_menu, create_user_state

class Telebot:
    def __init__(self, bot_token, api_token, engine, nlp):

        # Instantiate an updater
        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Link the reccomender engine
        self.engine = engine

        # Link the NER
        self.nlp = nlp

        # Add OMDB API token
        self.api_token = api_token

        # Setup dict for storing user state
        self.user_state = {}

        # Setuo the logger
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

        self.logger = logging.getLogger(__name__)

    def start(self, update, context):
        
        try:
            valid, button_list = self.button_list_generator()
            if valid:
                valid, menu = build_menu(button_list, n_cols=2)
            else:
                raise Exception("Error in button list generation")
            
            if valid is True:
                reply_markup = InlineKeyboardMarkup(menu)
                context.bot.send_message(chat_id=update.effective_chat.id, text='I am a bot', 
                                reply_markup=reply_markup)
                
        except Exception as error:
            print(error)

    def echo(self, update, context):
        
        # Check if user state is registered
        if udpate.effective_chat.id in self.user_state:
            # Load his state
            pass
        else:
            # Create a new state
            self.user_state[update.effective_chat.id] = create_user_state()
            

        plot = ""
        try:
            movie_title = get_movie_title(update.message.text)

            if movie_title == -1:
                raise Exception("Movie title could not be extracted")

            plot = get_plot(movie_title, self.api_token)

            if plot == -1:
                raise Exception("Movie not found in OMDB")
            
            
            movie_ids = self.engine.similar_movies(plot)
            
            movie_gen = get_movie_gen(movie_ids)

            while True:
                try:
                    movie_id = next(movie_gen)
                    movie_id = str(movie_id)
                                      
                    valid, title = get_metadata(movie_id, self.api_token)
                    
                    if valid is False:
                        print("SHIT")
                        print(movie_id)
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=title)
                
                except StopIteration:
                    break

            
        except Exception as error:
            print("Error occured")
            print(error)

        
        context.bot.send_message(chat_id=update.effective_chat.id, text=plot)

    def error(update, context):
        '''
        This function logs errors caused by updates
        '''
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def button_list_generator(self):
        '''
        This function generates button list
        '''
        try:
            button_list = [
                InlineKeyboardButton("I'll watch this", callback_data="Yes"),
                InlineKeyboardButton("Show me another", callback_data="No"),
                InlineKeyboardButton("Show me more information", callback_data="More"),                
            ]
        except Exception as error:
            return False, None
        finally:
            return True, button_list
            s
    def register_handlers(self):
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(Filters.text, self.echo)
        
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(echo_handler)

    def activate(self):
        self.register_handlers()
        self.updater.start_polling()
