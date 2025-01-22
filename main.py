import telebot
from telebot.types import Message, BotCommand
import json
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand("rep", "Збільшити репутацію. (тільки для адмінів)"),
    BotCommand("norep", "Зменшити репутацію. (тільки для адмінів)"),
    BotCommand("repboard", "Показати топ-5 користувачів за репутацією."),
])

REPUTATION_FILE = 'reputation.json'

def load_reputation():
    try:
        with open(REPUTATION_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_reputation(reputation):
    with open(REPUTATION_FILE, 'w') as f:
        json.dump(reputation, f, indent=4)

def update_reputation(user_id, chat_id, delta):
    reputation = load_reputation()
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)

    if chat_id_str not in reputation:
        reputation[chat_id_str] = {}

    if user_id_str not in reputation[chat_id_str]:
        reputation[chat_id_str][user_id_str] = 0

    reputation[chat_id_str][user_id_str] += delta
    save_reputation(reputation)

    return reputation[chat_id_str][user_id_str]

def is_admin(chat_id, user_id):
    member = bot.get_chat_member(chat_id, user_id)
    return member.status in ['administrator', 'creator']

@bot.message_handler(commands=['rep'])
def increase_rep(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "Тільки адміни можуть змінювати репутацію.")

    target_user = message.reply_to_message.from_user if message.reply_to_message else None
    if target_user:
        if is_admin(message.chat.id, target_user.id):
            bot.reply_to(message.chat.id, "Репутація адміністрації непохитно висока!")
        current_reputation = update_reputation(target_user.id, message.chat.id, 1)
        bot.reply_to(message, f"Репутація {target_user.first_name} збільшена на 1.\nПоточна репутація: {current_reputation}")
    else:
        bot.reply_to(message, "Використовуйте /rep у відповідь на повідомлення.")

@bot.message_handler(commands=['norep'])
def decrease_rep(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "Тільки адміни можуть змінювати репутацію.")

    target_user = message.reply_to_message.from_user if message.reply_to_message else None

    if target_user:
        if is_admin(message.chat.id, target_user.id):
            bot.reply_to(message.chat.id, "Репутація адміністрації непохитно висока!")
        current_reputation = update_reputation(target_user.id, message.chat.id, -1)
        bot.reply_to(message, f"Репутація {target_user.first_name} зменшена на 1.\nПоточна репутація: {current_reputation}")
    else:
        bot.reply_to(message, "Використовуйте /norep у відповідь на повідомлення.")

@bot.message_handler(commands=['repboard'])
def repboard(message: Message):
    reputation = load_reputation()
    chat_id_str = str(message.chat.id)
    
    if chat_id_str not in reputation:
        return bot.reply_to(message, "У цьому чаті ще немає даних про репутацію.")

    chat_reputation = reputation[chat_id_str]
    sorted_users = sorted(chat_reputation.items(), key=lambda x: x[1], reverse=True)

    top_5 = sorted_users[:5]
    board_message = "🏆 Топ 5 за репутацією:\n"
    for i, (user_id, rep) in enumerate(top_5, start=1):
        user = bot.get_chat_member(message.chat.id, user_id).user
        board_message += f"{i}. {user.first_name} - {rep} репутації\n"

    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user

    if str(target_user.id) not in [user[0] for user in top_5]:
        first_name = bot.get_chat_member(message.chat.id, target_user.id).user.first_name
        if is_admin(message.chat.id, target_user.id):
            board_message += f"{first_name} - НЕЙМОВІРНО БАГАТО РЕПУТАЦІЇ!"
        else:
            user_rep = chat_reputation.get(str(target_user.id), 0)
            user_position = sorted_users.index((target_user.id, user_rep)) + 1
            board_message += f"\n👤 {user_position}. {first_name} - {user_rep} репутації"

    bot.reply_to(message, board_message)

if __name__ == "__main__":
    bot.polling(non_stop=True)
