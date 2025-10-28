import os
import telebot
from telebot import types
import tempfile
import moviepy.editor as mp
import time
import requests

# 🔹 Токен из Render Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # пример: @KinoMania

bot = telebot.TeleBot(BOT_TOKEN)


# 🔹 Проверка подписки
def check_subscription(user_id):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        status = data.get("result", {}).get("status")
        return status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"[Ошибка проверки подписки]: {e}")
        return False


# 🔹 Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn_sub = types.InlineKeyboardButton("📺 Подписаться на KinoMania", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    markup.add(btn_sub)

    bot.send_message(
        message.chat.id,
        "👋 Привет! Это бот **KinoMania** 🎬\n\n"
        "Отправь мне видео, и я помогу обработать его.\n"
        "⚠️ Перед этим убедись, что ты подписан на наш канал.",
        reply_markup=markup
    )


# 🔹 Обработка видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id

    # Проверка подписки
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔔 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        markup.add(btn)
        bot.reply_to(
            message,
            "❌ Чтобы пользоваться ботом, подпишись на канал KinoMania!",
            reply_markup=markup
        )
        return

    msg = bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

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
