import os
import telebot
from telebot import types
from moviepy.editor import VideoFileClip
import threading
import http.server
import socketserver

# Получаем токен из переменной окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# === Обработка старта ===
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Отправь мне видео, и я уберу водяные знаки (или сделаю базовую очистку)."
    )

# === Обработка видео ===
@bot.message_handler(content_types=["video"])
def handle_video(message):
    try:
        bot.reply_to(message, "🎬 Видео получено. Начинаю обработку...")

        # Скачиваем видео
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, "wb") as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, "🧠 Обрабатываю видео, подожди немного...")

        # Пример обработки: обрезка 1 сек в начале и в конце (чтобы убрать водяной знак)
        clip = VideoFileClip(input_path)
        duration = clip.duration
        start_time = 1 if duration > 2 else 0
        end_time = duration - 1 if duration > 2 else duration

        processed_clip = clip.subclip(start_time, end_time)
        processed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        clip.close()
        processed_clip.close()

        # Отправляем готовое видео
        with open(output_path, "rb") as video:
            bot.send_video(message.chat.id, video, caption="✅ Видео обработано!")

        # Удаляем файлы после отправки
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")

# === Фейковый веб-сервер для Render (чтобы не ругался на порты) ===
def keep_alive():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Фейковый сервер запущен на порту {PORT}")
        httpd.serve_forever()

# === Запуск ===
if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    print("🤖 Бот запущен и ожидает сообщения...")
    bot.infinity_polling()
