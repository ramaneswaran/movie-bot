import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

# Import utility functions for API
from src.utils.api_utils import get_metadata, get_movie_detail, get_rating
from src.utils.api_utils import get_plot
from src.utils.bot_utils import build_menu, create_user_state
from src.utils.bot_utils import menu_one, menu_two, menu_three

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
            valid, button_list = menu_one()
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

    def button(self, update, context):
        '''
        This function handles callbacks from buttons
        '''
        data = update.callback_query.data
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id

        self.process_feedback(data, chat_id, message_id, context)

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
                                      
                    valid, data = get_metadata(movie_id, self.api_token)
                    
                    if valid is False:
                        print("SHIT")
                        print(movie_id)
                    else:
                        title = data['Title']
                        context.bot.send_message(chat_id=update.effective_chat.id, text=title)
                
                except StopIteration:
                    break

            
        except Exception as error:
            print("Error occured")
            print(error)

        
        context.bot.send_message(chat_id=update.effective_chat.id, text=plot)

    def process_feedback(self, data, chat_id, message_id, context):
        '''
        This function processes user feedback
        and calls another function to delegate work
        '''
        
        if data == 'Yes':
            print("Positive Feedback")
        elif data == 'No':
            print("Negative Feedback")
        elif data == 'More':
            print("Info requested")
            self.switch_menu(chat_id, message_id, 2, context)
        elif data == 'Director':
            print("Director info requested")
        elif data == 'Cast':
            print("Cast requested")
        elif data == 'Plot':
            print("Plot requested")
        elif data == 'Switch-1':
            self.switch_menu(chat_id, message_id, 1, context)
            print("Switch to menu 1")
        elif data == 'Switch-2':
            print("Switch to menu 2")


    def show_movie(self, chat_id, message_id):
        '''
        This function shows a movie
        '''
        pass

    def show_info(self, chat_id, info, message_id, context):
        '''
        This function shows more information
        '''
        try:
            # Get requested info
            info = self.user_state[chat_id]['movie']['info']

            # Build menu
            valid, button_list = menu_three()
            if not valid:
                raise Exception("Failed to get buttons")

            valid, menu = build_menu(button_list, 1)
            if not valid:
                raise Exception("Failed to build menu")

        except Exception as error:
            print(error)

        finally:
            reply_markup = InlineKeyboardMarkup(menu)
            context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=info, reply_markup=reply_markup)

    def switch_menu(self, chat_id, message_id, menu_number, context):
        '''
        This function switches menu
        '''
        try:
            if menu_number == 1:
                valid, button_list = menu_one()
                if not valid:
                    raise Exception("Failed to get buttons")
                
                valid, menu = build_menu(button_list, n_cols=2)
            
            elif menu_number == 2:
                valid, button_list = menu_two()
                if not valid:
                    raise Exception("Failed to get buttons")
                
                valid, menu = build_menu(button_list, n_cols=2)
            
            elif menu_number == 3:
                valid, button_list = menu_three()
                if not valid:
                    raise Exception("Failed to get buttons")

                valid, menu = build_menu(button_list, n_cols=1)
        
        except Exception as error:
            print(error)
        
        finally:
            
            reply_markup = InlineKeyboardMarkup(menu)
            context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, text='SHIT')
    
    def error(self, update, context):
        '''
        This function logs errors caused by updates
        '''
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)


    def register_handlers(self):
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(Filters.text, self.echo)
        button_handler = CallbackQueryHandler(self.button)
        
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(echo_handler)
        self.dispatcher.add_handler(button_handler)
        self.dispatcher.add_error_handler(self.error)

    def activate(self):
        self.register_handlers()
        self.updater.start_polling()
