import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Dispatcher

TOKEN = os.getenv("TOKEN")
URL = "https://movies-downloader-bot-ten-phi.vercel.app"
bot = Bot(TOKEN)
OWNER_USER_ID = "1932612943"


def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


def movie_result(update, context):
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)


def setup():
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', notify_owner))
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher


def notify_owner(update, context):
    user = update.message.from_user
    message = f"New user started the bot!\n\nUser Details:\nUsername: {user.username}\nName: {user.first_name} {user.last_name}\nUser ID: {user.id}"
    context.bot.send_message(chat_id=OWNER_USER_ID, text=message)


def create_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("⏫💕Our Official channel", url="https://t.me/bot_list_hub")],
        [InlineKeyboardButton("🔴Official Support Group💕", url="https://t.me/mehulsupport")],
        [InlineKeyboardButton("✅Developer", url="https://t.me/Patil_Mehul")]
    ]
    return InlineKeyboardMarkup(keyboard)


def welcome(update, context):
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to SB Movies.\n"
                              f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.\n \n Any problem than you should visit our support given below")
    update.message.reply_text("👇 Enter Movie Name 👇", reply_markup=create_inline_keyboard())


# Rest of the code remains the same


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


