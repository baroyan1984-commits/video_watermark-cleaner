import telebot
import requests
from moviepy.editor import VideoFileClip
import os
from flask import Flask
import threading

# --- Настройки ---
BOT_TOKEN = "7359754732:AAGdpBIOTLFoqzyj4z4zyTyfQRAA22a0w_4"
CHANNEL_INVITE_LINK = "https://t.me/Franglon"  # Пригласительная ссылка на канал

bot = telebot.TeleBot(BOT_TOKEN)

# --- Проверка подписки ---
def is_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member("@Franglon", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# --- Обработка команды /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        bot.reply_to(message, "✅ Добро пожаловать! Отправь видео, чтобы я его обработал 🎬")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        subscribe_btn = telebot.types.InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_INVITE_LINK)
        check_btn = telebot.types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")
        markup.add(subscribe_btn)
        markup.add(check_btn)
        bot.send_message(message.chat.id, "❗️Чтобы пользоваться ботом, подпишись на наш канал:", reply_markup=markup)

# --- Проверка подписки при нажатии кнопки ---
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.send_message(call.message.chat.id, "✅ Отлично! Теперь можешь отправить видео 🎬")
    else:
        bot.answer_callback_query(call.id, "❌ Ты ещё не подписан!")

# --- Обработка видео ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(message.chat.id, "❗️Сначала подпишись на канал, чтобы пользоваться ботом.")
        return

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = f"video_{user_id}.mp4"
    output_path = f"output_{user_id}.mp4"

    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "🎞 Обработка видео, подожди немного...")

    try:
        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path)
        with open(output_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке видео: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# --- Запуск бота ---
def start_bot():
    bot.infinity_polling()

# --- Flask-сервер для Render (не влияет на бота) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# --- Запуск ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot()
