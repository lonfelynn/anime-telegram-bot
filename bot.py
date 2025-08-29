import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import config
from logic import DB_Manager

bot = telebot.TeleBot(config.token)
db = DB_Manager(config.database)


def send_info(bot, message, row, favorite_view=False):
    ranked_id = row[3]
    info = f"""
📍 Title: {row[0]}
⭐ Score: {row[1]} (Votes: {row[2]})
🔥 Ranked: {row[3]}
🎞 Episodes: {row[5]}
📌 Status: {row[6]}
📅 Aired: {row[7]}
"""
    if favorite_view:
        bot.send_message(message.chat.id, info, reply_markup=remove_from_favorite(ranked_id))
    else:
        bot.send_message(message.chat.id, info, reply_markup=add_to_favorite(ranked_id))

def add_to_favorite(anime_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🌟 Add to favorites", callback_data=f'favorite_{anime_id}'))
    return markup

def remove_from_favorite(anime_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Remove from favorites", callback_data=f'remove_{anime_id}'))
    return markup

def main_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('/random'), KeyboardButton('/favorites'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    if call.data.startswith("favorite"):
        Ranked = int(call.data.split("_")[1])
        if db.add_favorite(user_id, Ranked):
            bot.answer_callback_query(call.id, "🌟 Added to your favorites!")
        else:
            bot.answer_callback_query(call.id, "⚠️ Already in your favorites!")

    elif call.data.startswith("remove"):
        Ranked = int(call.data.split("_")[1])
        db.remove_favorite(user_id, Ranked)
        bot.answer_callback_query(call.id, "❌ Removed from favorites!")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 
    """👋 Welcome to the Anime Bot 🎥
Here you can explore more than 1000 anime titles 🔥

👉 /random → Get a random anime
👉 Type part of the title to search 🎬
👉 /favorites → View saved anime 🌟
""", reply_markup=main_markup())

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
    """📖 *Help Menu*:
- /start → Welcome message
- /help → Show this help
- /random → Get a random anime
- Type part of an anime title to search (case-insensitive).
- /favorites → Show your saved favorites 🌟""", parse_mode="Markdown")

@bot.message_handler(commands=['random'])
def random_anime(message):
    rows = db.get_random_anime()
    if rows:
        send_info(bot, message, rows[0])

@bot.message_handler(commands=['favorites'])
def show_favorites(message):
    rows = db.get_favorites(message.from_user.id)
    if rows:
        bot.send_message(message.chat.id, f"🌟 Your favorites ({len(rows)}):")
        for row in rows: 
            send_info(bot, message, row, favorite_view=True)
    else:
        bot.send_message(message.chat.id, "❌ You don't have any favorites yet. Add some with the 🌟 button!")

@bot.message_handler(func=lambda message: True)
def search_anime(message):
    rows = db.search_anime(message.text)
    if rows:
        bot.send_message(message.chat.id, f"✅ Found {len(rows)} result(s).")
        for row in rows:  
            send_info(bot, message, row)
    else:
        bot.send_message(message.chat.id, "❌ Sorry, I couldn't find this anime.")


bot.infinity_polling()