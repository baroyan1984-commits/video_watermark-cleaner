import telebot
import os
import moviepy.editor as mp
import tempfile

TOKEN = os.getenv("BOT_TOKEN")  # ⚠️ Токен из .env или Render Environment
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
            temp_input.write(downloaded_file)
            temp_input_path = temp_input.name

        output_path = tempfile.mktemp(suffix=".mp4")

        bot.reply_to(message, "🎬 Обработка видео началась, подожди немного...")

        clip = mp.VideoFileClip(temp_input_path)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=2, verbose=False, logger=None)

        with open(output_path, "rb") as processed:
            bot.send_video(message.chat.id, processed)

        bot.reply_to(message, "✅ Готово! Водяные знаки удалены.")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

    finally:
        try:
            os.remove(temp_input_path)
            os.remove(output_path)
        except:
            pass


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Отправь мне видео, и я уберу водяной знак!")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling(skip_pending=True)
