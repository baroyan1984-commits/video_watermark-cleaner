import telebot
import os
import requests
from moviepy.editor import VideoFileClip

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

        # Получаем файл
        file_info = bot.get_file(message.video.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        input_path = "input.mp4"
        output_path = "output.mp4"

        # 1️⃣ Этап — загрузка
        progress_msg = bot.send_message(message.chat.id, "📥 [10%] Скачиваю видео...")
        r = requests.get(file_url)
        with open(input_path, 'wb') as f:
            f.write(r.content)

        bot.edit_message_text("⚙️ [30%] Видео скачано. Подготавливаю к обработке...", message.chat.id, progress_msg.message_id)

        # 2️⃣ Этап — обработка видео
        clip = VideoFileClip(input_path)
        bot.edit_message_text("🎞 [60%] Применяю обработку...", message.chat.id, progress_msg.message_id)

        # (Пример: просто перекодируем видео)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()

        bot.edit_message_text("🚀 [90%] Почти готово...", message.chat.id, progress_msg.message_id)

        # 3️⃣ Этап — отправка результата
        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f)

        bot.edit_message_text("✅ [100%] Готово! Видео успешно обработано 🎉", message.chat.id, progress_msg.message_id)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")

bot.polling(none_stop=True)
