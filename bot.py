import telebot
import os
import requests
import time
from moviepy.editor import VideoFileClip

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

        file_info = bot.get_file(message.video.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        input_path = "input.mp4"
        output_path = "output.mp4"

        progress_msg = bot.send_message(message.chat.id, "📥 [10%] Скачиваю видео...")
        r = requests.get(file_url)
        with open(input_path, 'wb') as f:
            f.write(r.content)

        bot.edit_message_text("⚙️ [30%] Видео скачано. Подготавливаю к обработке...", message.chat.id, progress_msg.message_id)
        time.sleep(1)

        bot.edit_message_text("🎞 [60%] Применяю обработку...", message.chat.id, progress_msg.message_id)
        time.sleep(2)

        # ✅ открываем файл ОДИН раз
        clip = VideoFileClip(input_path)
        duration = min(clip.duration, 5)  # ограничим длину до 5 секунд для Render Free
        processed_clip = clip.subclip(0, duration)
        processed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()
        processed_clip.close()

        bot.edit_message_text("🚀 [90%] Почти готово...", message.chat.id, progress_msg.message_id)
        time.sleep(1)

        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f)

        bot.edit_message_text("✅ [100%] Готово! Видео успешно обработано 🎉", message.chat.id, progress_msg.message_id)

        # Удаляем временные файлы
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")

bot.polling(none_stop=True)
