import telebot
import os
from moviepy.editor import VideoFileClip

# === Укажи свой токен бота ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render возьмёт токен из переменных окружения
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "👋 Привет! Отправь мне видео, и я обработаю его (обрежу первые 3 секунды).")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        bot.reply_to(message, "📥 Получаю видео...")
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        filename = f"/tmp/{message.video.file_unique_id}.mp4"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "🎞 Видео получено! Начинаю обработку...")

        processed_file = f"/tmp/processed_{message.video.file_unique_id}.mp4"

        # === Обрезаем первые 3 секунды ===
        clip = VideoFileClip(filename)
        duration = clip.duration

        if duration > 3:
            processed_clip = clip.subclip(3, duration)
        else:
            processed_clip = clip  # если короткое видео — оставляем как есть

        processed_clip.write_videofile(processed_file, codec="libx264", audio_codec="aac")
        clip.close()
        processed_clip.close()

        # === Отправляем обратно ===
        with open(processed_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid)

        bot.reply_to(message, "✅ Готово! Видео обработано и отправлено обратно.")

        # === Удаляем временные файлы ===
        os.remove(filename)
        os.remove(processed_file)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке видео: {e}")

# === Запуск бота ===
bot.polling(none_stop=True)
