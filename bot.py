import os
import telebot
from telebot import types
from moviepy.editor import VideoFileClip
import threading
import http.server
import socketserver
import time

# === Telegram Bot Token ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# === Функция обработки видео с динамическим прогрессом ===
def process_video(chat_id, input_path, output_path):
    try:
        bot.send_message(chat_id, "📽️ Видео получено. Начинаю обработку...")

        clip = VideoFileClip(input_path)
        duration = clip.duration
        start_time = 1 if duration > 2 else 0
        end_time = duration - 1 if duration > 2 else duration
        subclip = clip.subclip(start_time, end_time)

        bot.send_message(chat_id, "⚙️ Начинаю применять фильтры...")

        # === Генерация видео с динамическим прогрессом ===
        total_frames = subclip.reader.nframes
        progress_message = bot.send_message(chat_id, "🔄 Прогресс: 0%")
        last_percent = 0

        def update_progress(current_frame, total):
            nonlocal last_percent
            percent = int((current_frame / total) * 100)
            if percent - last_percent >= 10:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_message.message_id,
                    text=f"🔄 Прогресс: {percent}%"
                )
                last_percent = percent

        # === Запись видео с прогрессом ===
        for i, frame in enumerate(subclip.iter_frames()):
            update_progress(i, total_frames)

        subclip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=2, logger=None)

        # Финальное сообщение
        bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text="✅ Прогресс: 100%")

        clip.close()
        subclip.close()

        with open(output_path, "rb") as video:
            bot.send_video(chat_id, video, caption="🎉 Готово! Водяной знак удалён ✅")

        os.remove(input_path)
        os.remove(output_path)

        bot.send_message(chat_id, "🧹 Очистка завершена. Видео успешно обработано!")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка при обработке: {e}")

# === Обработка команды /start ===
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "👋 Привет! Отправь мне видео — я удалю водяные знаки и обработаю его.")

# === Приём видео ===
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

        threading.Thread(target=process_video, args=(chat_id, input_path, output_path)).start()

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {e}")

# === Keep-alive сервер для Render ===
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
