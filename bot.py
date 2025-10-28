import os
import telebot
from moviepy.editor import VideoFileClip

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=["video"])
def handle_video(message):
    bot.reply_to(message, "🎬 Видео получено. Начинаю обработку...")

    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        with open(input_path, "wb") as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, "⚙️ Обрабатываю видео, подожди немного...")

        # 🔹 Простая безопасная обработка (без зависаний)
        clip = VideoFileClip(input_path).subclip(0, min(clip.duration, 5))
        output_path = "output.mp4"
        clip.write_videofile(output_path, codec="libx264", audio=False, fps=24, verbose=False, logger=None)
        clip.close()

        with open(output_path, "rb") as video:
            bot.send_video(message.chat.id, video)
        bot.send_message(message.chat.id, "✅ Готово!")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

bot.polling(non_stop=True)
