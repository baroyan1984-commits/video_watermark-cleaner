import os
import telebot
from moviepy.editor import VideoFileClip
from flask import Flask, request

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Обработка видео ===
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        chat_id = message.chat.id
        bot.reply_to(message, "🎬 Видео получено, начинаю обработку...")
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, 'wb') as f:
            f.write(downloaded_file)

        bot.send_message(chat_id, "⚙️ Обрабатываю видео, подожди немного...")

        # Пример обработки — удаляем аудио
        clip = VideoFileClip(input_path)
        clip = clip.without_audio()
        clip.write_videofile(output_path, codec='libx264', audio=False)

        bot.send_message(chat_id, "✅ Видео обработано, отправляю результат...")
        with open(output_path, 'rb') as f:
            bot.send_video(chat_id, f)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")

# === Flask Webhook ===
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return '🤖 Бот работает через Webhook!', 200

# === Запуск ===
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    # Удаляем старый webhook (если был)
    bot.remove_webhook()

    # Устанавливаем новый webhook
    WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.set_webhook(url=WEBHOOK_URL)

    print(f"✅ Webhook установлен: {WEBHOOK_URL}")
    app.run(host='0.0.0.0', port=8080)
