from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters



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
        
        doc = self.nlp(update.message.text)
        
        message = ""
        try:
            movie_name = doc.ents[0].text
            message = "So you liked "+movie_name
        except Exception as error:
            print(error)

        
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    

    def register_handlers(self):
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(Filters.text, self.echo)
        
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(echo_handler)

    def activate(self):
        self.register_handlers()
        self.updater.start_polling()
