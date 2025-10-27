
import os
import telebot
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: TELEGRAM_TOKEN env var is not set")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, "👋 Бот запущен. Пришли видео или сообщение.")

@bot.message_handler(content_types=['text'])
def echo_text(message):
    bot.reply_to(message, "Я получил сообщение. Пришли видео, и я сохраню его на сервере.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        bot.reply_to(message, "🎬 Видео получено! Загружаю на сервер...")

        file_info = bot.get_file(message.video.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        filename = f"/tmp/{message.video.file_unique_id}.mp4"

        r = requests.get(file_url, stream=True, timeout=60)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        bot.reply_to(message, f"✅ Видео сохранено как {os.path.basename(filename)}. (Обработка пока не подключена)")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Бот стартует...")
    bot.polling(none_stop=True)

