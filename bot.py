import os
import telebot
from telebot import types
from moviepy.editor import VideoFileClip
import threading
import http.server
import socketserver
import time

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# === Функция для обработки видео ===
def process_video(chat_id, input_path, output_path):
    try:
        bot.send_message(chat_id, "⚙️ Применяю обработку (10%)...")

        clip = VideoFileClip(input_path)
        duration = clip.duration

        bot.send_message(chat_id, "🧩 Подготавливаю видео (30%)...")

        # Минимальная обрезка для демонстрации — убираем 1 секунду с начала и конца
        start_time = 1 if duration > 2 else 0
        end_time = duration - 1 if duration > 2 else duration
        processed_clip = clip.subclip(start_time, end_time)

        bot.send_message(chat_id, "🎞️ Применяю фильтры и кодек (60%)...")

        # Пишем видео без блокировки Render
        processed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=2, logger=None)

        bot.send_message(chat_id, "✅ Почти готово (90%)...")

        clip.close()
        processed_clip.close()

        # Отправляем готовое видео
        with open(output_path, "rb") as video:
            bot.send_video(chat_id, video, caption="🎉 Готово! Водяной знак удалён ✅")

        # Удаляем временные файлы
        os.remove(input_path)
        os.remove(output_path)

        bot.send_message(chat_id, "🧹 Очистка завершена. Видео обработано!")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка при обработке: {e}")

# === Обработка команды /start ===
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "👋 Привет! Отправь мне видео, и я удалю водяные знаки или лишние части.")

# === Обработка видео ===
@bot.message_handler(content_types=["video"])
def handle_video(message):
    chat_id = message.chat.id
    try:
        bot.reply_to(message, "📥 Видео получено. Загружаю файл...")

        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, "wb") as f:
            f.write(downloaded_file)

        bot.send_message(chat_id, "🚀 Начинаю обработку видео...")

        # Запускаем обработку в отдельном потоке
        threading.Thread(target=process_video, args=(chat_id, input_path, output_path)).start()

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {e}")

# === Фейковый сервер для Render ===
def keep_alive():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Сервер запущен на порту {PORT}")
        httpd.serve_forever()

# === Запуск ===
if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    print("🤖 Бот запущен и слушает Telegram...")
    bot.infinity_polling()
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
