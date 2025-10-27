# bot.py
import os
import telebot
from moviepy.editor import VideoFileClip
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")  # имя переменной окружения в Render
if not BOT_TOKEN:
    raise SystemExit("ERROR: BOT_TOKEN env var is not set")

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)  # threaded=False для webhook

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return '🤖 Bot via webhook is running', 200

@bot.message_handler(commands=['start'])
def start_cmd(m):
    bot.reply_to(m, "Привет — бот через webhook запущен. Пришли видео.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, "🎬 Видео получено, скачиваю...")
        file_info = bot.get_file(message.video.file_id)
        file_bytes = bot.download_file(file_info.file_path)

        input_path = f"/tmp/{message.video.file_unique_id}.mp4"
        output_path = f"/tmp/{message.video.file_unique_id}_out.mp4"

        with open(input_path, "wb") as f:
            f.write(file_bytes)

        bot.send_message(chat_id, "⚙️ Обрабатываю видео (пример: удаляю аудио)...")
        clip = VideoFileClip(input_path)
        clip = clip.without_audio()
        clip.write_videofile(output_path, codec="libx264", audio=False, threads=1)

        bot.send_message(chat_id, "✅ Готово, отправляю...")
        with open(output_path, "rb") as vid:
            bot.send_video(chat_id, vid)

        clip.close()
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка при обработке: {e}")

if __name__ == "__main__":
    # IMPORTANT: Render provides $PORT env var. используем её
    port = int(os.environ.get("PORT", 8080))
    # Удаляем старый webhook (если есть) и устанавливаем новый webhook на адрес Render
    try:
        bot.remove_webhook()
    except Exception:
        pass

    external = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # Render сам задаёт
    if external:
        webhook_url = f"https://{external}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        print("Webhook set to:", webhook_url)
    else:
        print("RENDER_EXTERNAL_HOSTNAME not defined — webhook установить не удалось (локально).")

    app.run(host="0.0.0.0", port=port)
