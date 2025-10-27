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

        # Получаем ссылку на видео с серверов Telegram
        file_info = bot.get_file(message.video.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        input_path = "input.mp4"
        output_path = "output.mp4"

        # Скачиваем видео
        r = requests.get(file_url)
        with open(input_path, 'wb') as f:
            f.write(r.content)

        bot.send_message(message.chat.id, "⏳ Обрабатываю видео, подожди немного...")

        # Обработка видео (пока просто конвертация)
        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()

        bot.send_message(message.chat.id, "✅ Готово! Отправляю обратно...")

        with open(output_path, 'rb') as f:
            bot.send_video(message.chat.id, f)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")

bot.polling(none_stop=True)
