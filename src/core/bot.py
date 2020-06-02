import logging
import telegram
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
from src.utils.bot_utils import get_movie_title
from src.utils.bot_utils import get_movie_gen

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
        if update.effective_chat.id in self.user_state:
            # Load his state
            pass
        else:
            # Create a new state
            self.user_state[update.effective_chat.id] = create_user_state()
       
        try:
            
            doc = self.nlp(update.message.text)
            valid, movie_title = get_movie_title(doc)

            if not valid:
                raise Exception("Movie title could not be extracted")

            print("Movie title is : "+movie_title)

            valid, plot = get_plot(movie_title, self.api_token)
            
            if not valid:
                raise Exception("Movie not found in OMDB")
            print("Movie plot is :"+plot)

            # Get similar movies
            movie_ids = self.engine.similar_movies(plot)
            print(movie_ids)
            # Get a movie generator
            movie_gen = get_movie_gen(movie_ids)

            # Load the user state
            self.user_state[update.effective_chat.id]['request'] = True
            self.user_state[update.effective_chat.id]['gen'] = movie_gen

            
        except Exception as error:
            print("Error occured")
            print(error)

        finally:
            self.show_movie(update.effective_chat.id, context)

    def process_feedback(self, data, chat_id, message_id, context):
        '''
        This function processes user feedback
        and calls another function to delegate work
        '''
        
        if data == 'Yes':
            print("Positive Feedback")
        elif data == 'No':
            self.show_movie(chat_id, context)
            print("Negative Feedback")
        elif data == 'More':
            print("Info requested")
            self.switch_menu(chat_id, message_id, 2, context)
        elif data == 'Director':
            self.show_info(chat_id, 'Director', message_id, context)
            print("Director info requested")
        elif data == 'Cast':
            self.show_info(chat_id, 'Actors', message_id, context)
            print("Cast requested")
        elif data == 'Plot':
            self.show_info(chat_id, 'Plot', message_id, context)
            print("Plot requested")
        elif data == 'Rating':
            print("Rating requested")
        elif data == 'Switch-1':
            self.switch_menu(chat_id, message_id, 1, context)
            print("Switch to menu 1")
        elif data == 'Switch-2':
            self.switch_menu(chat_id, message_id, 2, context)
            print("Switch to menu 2")


    def show_movie(self, chat_id, context):
        '''
        This function shows a movie
        '''
        try:
            # Check if user has requested movie
            if self.user_state[chat_id]['request'] is False:
                raise Exception("No movie request made")
            
            # Get the generator
            movie_gen = self.user_state[chat_id]['gen']

            # Load a movie to user state
            movie_id = next(movie_gen)
            movie_id = str(movie_id)

            valid, data = get_metadata(movie_id, self.api_token)

            if not valid:
                raise Exception("API call failed")

            self.user_state[chat_id]['movie'] = data

            title = data['Title']
            runtime = data['Runtime']
            year = data['Year']
            rated = data['Rated']
            poster = data['Poster']

            # Contruct the message
            message = "<b>"+title+"</b> \n"
            message += "\n"
            message += "<b>Year   :</b> \t"+year+"\n"
            message += "<b>Rated  :</b> \t"+rated+"\n"
            message += "<b>Runtime:</b> \t"+runtime+"\n"
            
            # Contruct menu
            valid, button_list = menu_one()
            if not valid:
                print("Failed to get buttons")
            
            valid, menu = build_menu(button_list, 2)
            if not valid:
                print("Failed to build menu")

            reply_markup = InlineKeyboardMarkup(menu)

            # Send message
            context.bot.send_photo(chat_id=chat_id, photo=poster)
            context.bot.send_message(chat_id=chat_id, text=message, 
                                    parse_mode=telegram.ParseMode.HTML,
                                    reply_markup=reply_markup)

        except StopIteration:
            context.bot.send_message(chat_id=chat_id, text="That's all folks")

        except Exception as error:
            print(error)



    def show_info(self, chat_id, info, message_id, context):
        '''
        This function shows more information
        '''
        try:
            # Get requested info
            fetched_info = self.user_state[chat_id]['movie'][info]

            # Build menu
            valid, button_list = menu_three()
            if not valid:
                raise Exception("Failed to get buttons")

            valid, menu = build_menu(button_list, 1)
            if not valid:
                raise Exception("Failed to build menu")
            
            reply_markup = InlineKeyboardMarkup(menu)
            
            # Construct message
            message = "<b>"+info+"</b>\n\n"
            message += fetched_info

            context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                            text=message, reply_markup=reply_markup,
                            parse_mode=telegram.ParseMode.HTML)

        except Exception as error:
            print(error)

            
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

                if not valid:
                    raise Exception("Failed to build menu")

                data = self.user_state[chat_id]['movie']

                title = data['Title']
                runtime = data['Runtime']
                year = data['Year']
                rated = data['Rated']
                poster = data['Poster']

                # Contruct the message
                message = "<b>"+title+"</b> \n"
                message += "\n"
                message += "<b>Year   :</b> \t"+year+"\n"
                message += "<b>Rated  :</b> \t"+rated+"\n"
                message += "<b>Runtime:</b> \t"+runtime+"\n"


            
                reply_markup = InlineKeyboardMarkup(menu)
                context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                                reply_markup=reply_markup, text=message,
                                parse_mode=telegram.ParseMode.HTML)

            
            elif menu_number == 2:
                valid, button_list = menu_two()
                if not valid:
                    raise Exception("Failed to get buttons")
                
                valid, menu = build_menu(button_list, n_cols=2)

                if not valid:
                    raise Exception("Failed to build menu")

                reply_markup = InlineKeyboardMarkup(menu)
                context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, text="What do you want to know?")

        
        except Exception as error:
            print(error)
    
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
