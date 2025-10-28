import telebot
from telebot import types
import os
import requests
from moviepy.editor import VideoFileClip
from flask import Flask

# Токен твоего бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "7359754732:AAGdpBIOTLFoqzyj4z4zyTyfQRAA22a0w_4")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 🔗 Новая пригласительная ссылка на канал
CHANNEL_INVITE_LINK = "https://t.me/Franglon"
CHANNEL_USERNAME = "@Franglon"

@app.route('/')
def home():
    return "✅ Bot is running!"

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🔔 Подписаться на канал", url=CHANNEL_INVITE_LINK)
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "👋 Привет!\nЧтобы пользоваться ботом, подпишись на наш канал 👇",
        reply_markup=markup
    )

# Проверка подписки
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

# Обработка видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id

    # Проверяем подписку
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔔 Подписаться на канал", url=CHANNEL_INVITE_LINK)
        markup.add(btn)
        bot.reply_to(message, "Чтобы использовать бота, сначала подпишись на канал 👇", reply_markup=markup)
        return

    # Сохраняем видео
    file_info = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = "input_video.mp4"
    output_path = "output_video.mp4"

    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Обрабатываем видео
    try:
        clip = VideoFileClip(input_path)
        clip = clip.subclip(0, clip.duration)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        clip.close()

        with open(output_path, 'rb') as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке видео: {e}")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# Flask сервер для Render
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: bot.polling(non_stop=True)).start()
    app.run(host="0.0.0.0", port=10000)
    try:
        # Сохраняем видео во временный файл
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_input.write(downloaded_file)
        temp_input.close()
        input_path = temp_input.name
        output_path = tempfile.mktemp(suffix=".mp4")

        # 🔄 Индикатор прогресса
        def update_progress(percent, text):
            total_blocks = 10
            filled_blocks = int(percent / 10)
            bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
            bot.edit_message_text(
                f"{text}\n\n{bar} {percent}%",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )

        update_progress(10, "📥 Загружаю видео...")
        time.sleep(1)
        update_progress(40, "🎞 Обрабатываю кадры...")
        time.sleep(1)

        clip = mp.VideoFileClip(input_path)
        processed_clip = clip.subclip(0, min(clip.duration, 10))  # ограничим 10 сек
        update_progress(70, "⚙️ Оптимизация качества...")
        time.sleep(1)

        processed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        update_progress(100, "✅ Обработка завершена!")

        # Отправляем готовое видео
        with open(output_path, "rb") as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="🎉 Готово! Подпишись на канал @KinoMania — там самые крутые инструменты 🎬"
            )

        clip.close()
        processed_clip.close()
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка обработки: {e}")


# 🔹 Ответ по умолчанию
@bot.message_handler(func=lambda m: True)
def default_response(message):
    bot.send_message(message.chat.id, "📹 Просто отправь видео, и я обработаю его ✨")


if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling(skip_pending=True)
