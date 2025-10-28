import telebot
from telebot import types
import os
from moviepy.editor import VideoFileClip
from flask import Flask
import threading

# === Настройки ===
BOT_TOKEN = "7359754732:AAGdpBIOTLFoqzyj4z4zyTyfQRAA22a0w_4"
CHANNEL_USERNAME = "@Franglon"  # username канала
CHANNEL_INVITE_LINK = "https://t.me/Franglon"  # ссылка-приглашение

bot = telebot.TeleBot(BOT_TOKEN)

# === Проверка подписки ===
def is_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# === Команда /start ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        bot.send_message(message.chat.id, "✅ Добро пожаловать! Отправь видео, и я удалю водяной знак 🎬")
    else:
        markup = types.InlineKeyboardMarkup()
        subscribe = types.InlineKeyboardButton("📢 Подписаться", url=CHANNEL_INVITE_LINK)
        check = types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")
        markup.add(subscribe)
        markup.add(check)
        bot.send_message(message.chat.id, "❗️Чтобы пользоваться ботом, подпишись на канал:", reply_markup=markup)

# === Проверка кнопки ===
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.send_message(call.message.chat.id, "✅ Отлично! Теперь отправь видео 🎞")
    else:
        bot.answer_callback_query(call.id, "❌ Ты ещё не подписан!")

# === Обработка видео ===
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(message.chat.id, "⚠️ Подпишись на канал, чтобы пользоваться ботом.")
        return

    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = f"input_{user_id}.mp4"
    output_path = f"output_{user_id}.mp4"

    with open(input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    bot.send_message(message.chat.id, "🎬 Обработка видео...")

    try:
        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()

        with open(output_path, "rb") as video:
            bot.send_video(message.chat.id, video)
        bot.send_message(message.chat.id, "✅ Готово! Водяные знаки удалены.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# === Flask для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot.infinity_polling(skip_pending=True)

# === Запуск ===
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
