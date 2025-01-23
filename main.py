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

def get_target_user(message: Message):
    target_user = None
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        target_user = message.from_user
    
    return target_user

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

def clear_repboard(chat_id):
    reputation = load_reputation()
    chat_id_str = str(chat_id)

    if chat_id_str in reputation:
        if 'data' in reputation[chat_id_str]:
            try:
                bot.delete_message(chat_id, reputation[chat_id_str]["data"]["last_call"])
                bot.delete_message(chat_id, reputation[chat_id_str]["data"]["last_repboard"])
            except:
                pass

    save_reputation(reputation)

def write_repboard(chat_id, call_id, message_id):
    reputation = load_reputation()
    chat_id_str = str(chat_id)

    if chat_id_str in reputation:
        reputation[chat_id_str]['data'] = {}
        reputation[chat_id_str]['data']['last_call'] = call_id
        reputation[chat_id_str]['data']['last_repboard'] = message_id

    save_reputation(reputation)

def has_info(chat_id):
    reputation = load_reputation()
    chat_id_str = str(chat_id)
    return chat_id_str in reputation

def format_repboard(chat_id, target_user=None):
    reputation = load_reputation()
    chat_id_str = str(chat_id)

    chat_reputation = reputation[chat_id_str]
    chat_reputation.pop('data', None)

    sorted_users = sorted(chat_reputation.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_users[:5]

    board_message = "🏆 Топ 5 за репутацією:\n"
    for i, (user_id, rep) in enumerate(top_5, start=1):
        user = bot.get_chat_member(chat_id, user_id).user
        board_message += f"{i}. {user.first_name} - {rep} репутації\n"

    if target_user and str(target_user.id) not in [user[0] for user in top_5]:
        if is_admin(chat_id, target_user.id):
            board_message += f"\n{target_user.first_name} - НЕЙМОВІРНО БАГАТО РЕПУТАЦІЇ!"
        else:
            user_rep = chat_reputation.get(str(target_user.id), 0)
            user_position = sorted_users.index((target_user.id, user_rep)) + 1
            board_message += f"\n👤 {user_position}. {target_user.first_name} - {user_rep} репутації"

    return board_message

def is_admin(chat_id, user_id):
    member = bot.get_chat_member(chat_id, user_id)
    return member.status in ['administrator', 'creator']

@bot.message_handler(commands=['rep'])
def increase_rep(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        # return bot.reply_to(message, "Тільки адміни можуть змінювати репутацію.")
        return bot.delete_message(message.chat.id, message.id)

    target_user = get_target_user(message)

    if bot.get_me().id == target_user.id:
        return bot.reply_to(message, "Моя репутація непохитна!")

    if target_user:
        if is_admin(message.chat.id, target_user.id):
            bot.reply_to(message, "Репутація адміністрації непохитно висока!")
        else:
            current_reputation = update_reputation(target_user.id, message.chat.id, 1)
            bot.reply_to(message, f"Репутація {target_user.first_name} збільшена на 1.\nПоточна репутація: {current_reputation}")
    else:
        bot.reply_to(message, "Використовуйте /rep у відповідь на повідомлення.")


@bot.message_handler(commands=['norep'])
def decrease_rep(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        # return bot.reply_to(message, "Тільки адміни можуть змінювати репутацію.")
        return bot.delete_message(message.chat.id, message.id)

    target_user = get_target_user(message)

    if bot.get_me().id == target_user.id:
        return bot.reply_to(message, "Моя репутація непохитна!")

    if target_user:
        if is_admin(message.chat.id, target_user.id):
            bot.reply_to(message, "Репутація адміністрації непохитно висока!")
        else:
            current_reputation = update_reputation(target_user.id, message.chat.id, -1)
            bot.reply_to(message, f"Репутація {target_user.first_name} зменшена на 1.\nПоточна репутація: {current_reputation}")
    else:
        bot.reply_to(message, "Використовуйте /norep у відповідь на повідомлення.")


@bot.message_handler(commands=['repboard'])
def repboard(message: Message):
    clear_repboard(message.chat.id)
    
    if not has_info(message.chat.id):
        return bot.reply_to(message, "У цьому чаті ще немає даних про репутацію.")

    target_user = get_target_user(message)
    board_message = format_repboard(message.chat.id, target_user)

    bot_message = bot.reply_to(message, board_message)

    write_repboard(message.chat.id, message.id, bot_message.id)

if __name__ == "__main__":
    bot.polling(non_stop=True)
