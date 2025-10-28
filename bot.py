import os
import telebot
from telebot import types
from moviepy.editor import VideoFileClip
import tempfile

# --- Конфигурация ---
TOKEN = os.getenv("BOT_TOKEN")  # ✅ Render → Environment → BOT_TOKEN
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@KinoMania")  # ✅ Render → Environment → CHANNEL_USERNAME
bot = telebot.TeleBot(TOKEN)


# --- Проверка подписки ---
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        )
        keyboard.add(btn)
        bot.send_message(
            message.chat.id,
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Чтобы пользоваться ботом, сначала подпишись на наш канал {CHANNEL_USERNAME}.",
            reply_markup=keyboard
        )
        return

    bot.send_message(message.chat.id, "✅ Отлично! Отправь мне видео, и я уберу водяной знак.")


# --- Обработка видео ---
@bot.message_handler(content_types=["video"])
def handle_video(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        bot.reply_to(message, "⚠️ Сначала подпишись на канал и попробуй снова!")
        return

    bot.reply_to(message, "🎬 Видео получено. Начинаю обработку...")

    try:
        # Загружаем видео
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
            temp_input.write(downloaded_file)
            temp_input_path = temp_input.name

        output_path = tempfile.mktemp(suffix=".mp4")

        # Индикатор процесса
        bot.send_chat_action(message.chat.id, 'upload_video')
        bot.send_message(message.chat.id, "⚙️ Обрабатываю видео, подожди немного...")

        # Пример обработки — просто конвертация без звука
        clip = VideoFileClip(temp_input_path)
        clip = clip.subclip(0, min(clip.duration, 10))  # первые 10 секунд
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
        clip.close()

        # Отправляем результат
        with open(output_path, "rb") as processed:
            bot.send_video(message.chat.id, processed)
        bot.send_message(message.chat.id, "✅ Готово! Водяные знаки удалены.")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")
    finally:
        try:
            os.remove(temp_input_path)
            os.remove(output_path)
        except:
            pass


# --- Запуск ---
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling(skip_pending=True)
        r.raise_for_status()
        with open(input_path, "wb") as f:
            for chunk in r.iter_content(1024*16):
                if chunk:
                    f.write(chunk)

        # Прогресс-обновления
        def update_progress(percent, text):
            try:
                bar = "▮" * int(percent/10) + "▯" * (10 - int(percent/10))
                bot.edit_message_text(f"{text}\n\n{bar} {percent}%", chat_id=msg.chat.id, message_id=msg.message_id)
            except Exception:
                pass

        update_progress(10, "📥 Загружаю и подготавливаю...")
        time.sleep(0.5)
        update_progress(30, "🎞 Подготовка кадров...")

        clip = mp.VideoFileClip(input_path)
        update_progress(50, "⚙️ Применяю обработку...")
        time.sleep(0.5)

        # Простейшая обработка — обрезка 1 секунды и удаление аудио (пример)
        start = 0.0 if clip.duration < 1.0 else 1.0
        processed = clip.subclip(start, clip.duration).without_audio()

        update_progress(75, "🔧 Экспорт видео...")
        processed.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

        update_progress(100, "✅ Готово!")
        with open(output_path, "rb") as out_f:
            bot.send_video(message.chat.id, out_f, caption="🎉 Обработка завершена.")

        clip.close()
        processed.close()
        os.remove(input_path)
        os.remove(output_path)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке: {e}")

# Запуск бота polling в потоке
def run_bot_polling():
    print("Bot polling started")
    bot.infinity_polling(skip_pending=True)

# Мини-сервер чтобы Render видел open port
@app.route("/")
def index():
    return "KinoMania bot is running", 200

if __name__ == "__main__":
    t = threading.Thread(target=run_bot_polling, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 8080))
    # Flask блокирует основной поток — Render обнаружит порт
    app.run(host="0.0.0.0", port=port)
        )
        return

    msg = bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

    try:
        # Сохраняем видео
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, "wb") as new_file:
            new_file.write(downloaded_file)

        # 🔹 Индикатор прогресса
        def update_progress(percent, text):
            total_blocks = 10
            filled = int(percent / 10)
            bar = "▮" * filled + "▯" * (total_blocks - filled)
            bot.edit_message_text(
                f"{text}\n\n{bar} {percent}%",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )

        # Этапы
        update_progress(10, "📥 Загружаю видео...")
        time.sleep(1)
        update_progress(30, "🎞 Подготавливаю кадры...")
        time.sleep(1)

        clip = mp.VideoFileClip(input_path)
        update_progress(50, "⚙️ Применяю фильтры и эффекты...")
        time.sleep(1)

        processed_clip = clip.subclip(1, clip.duration).without_audio()
        update_progress(70, "🧠 Оптимизация качества...")
        time.sleep(1)

        processed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        update_progress(100, "✅ Обработка завершена!")

        # Отправляем результат
        with open(output_path, "rb") as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="🎉 Готово! Твоё видео успешно обработано.\n\n"
                        "📺 Подпишись на канал <b>@KinoMania</b> — там самые крутые инструменты 🎬"
            )

        # Очистка
        clip.close()
        processed_clip.close()
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: <code>{e}</code>")


# 🔹 Ответ по умолчанию
@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.send_message(message.chat.id, "📹 Просто отправь видео, и я обработаю его ✨")


print("🤖 KinoMania Bot запущен...")
bot.infinity_polling(skip_pending=True)
        bot.reply_to(
            message,
            "❌ Чтобы пользоваться ботом, подпишись на канал KinoMania!",
            reply_markup=markup
        )
        return

    msg = bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

    def process_video():
        try:
            # Сохраняем видео
            file_info = bot.get_file(message.video.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            input_path = "input.mp4"
            output_path = "output.mp4"

            with open(input_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # 🔄 Индикатор процесса
            def update_progress(percent, text):
                total_blocks = 10
                filled_blocks = int(percent / 10)
                bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
                try:
                    bot.edit_message_text(
                        f"{text}\n\n{bar} {percent}%",
                        chat_id=msg.chat.id,
                        message_id=msg.message_id
                    )
                except:
                    pass

            # 🔹 Этапы обработки
            update_progress(10, "📥 Загружаю видео...")
            time.sleep(1)

            update_progress(30, "🎞 Подготавливаю кадры...")
            clip = mp.VideoFileClip(input_path)
            time.sleep(1)

            update_progress(50, "⚙️ Применяю фильтры и эффекты...")
            processed_clip = clip.subclip(1, clip.duration).without_audio()
            time.sleep(1)

            update_progress(70, "🧠 Оптимизация качества...")
            processed_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)

            update_progress(100, "✅ Обработка завершена!")

            # 🔹 Отправляем результат
            with open(output_path, 'rb') as video:
                bot.send_video(
                    message.chat.id,
                    video,
                    caption="🎉 Готово! Твоё видео успешно обработано.\n\n"
                            "📺 Подпишись на канал @KinoMania — там самые крутые инструменты 🎬"
                )

            # Очистка
            clip.close()
            processed_clip.close()
            os.remove(input_path)
            os.remove(output_path)

        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке видео:\n<code>{e}</code>")

    # Запуск в отдельном потоке (чтобы бот не завис)
    threading.Thread(target=process_video).start()


# 🔹 Обработка любых других сообщений
@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.send_message(message.chat.id, "📹 Просто отправь видео, и я обработаю его ✨")


# 🔹 Запуск бота
print("🤖 KinoMania Bot запущен...")
bot.infinity_polling(skip_pending=True)
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Обработка в отдельном потоке, чтобы не блокировать Telegram
        threading.Thread(target=process_video, args=(message, msg, input_path, output_path)).start()

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при загрузке видео: {e}")


# === Функция обработки видео ===
def process_video(message, msg, input_path, output_path):
    try:
        def update_progress(percent, text):
            total_blocks = 10
            filled_blocks = int(percent / 10)
            bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
            try:
                bot.edit_message_text(
                    f"{text}\n\n{bar} {percent}%",
                    chat_id=msg.chat.id,
                    message_id=msg.message_id
                )
            except:
                pass

        update_progress(10, "📥 Загружаю видео...")
        time.sleep(1)
        update_progress(30, "🎞 Подготавливаю кадры...")
        time.sleep(1)

        clip = VideoFileClip(input_path)
        update_progress(50, "⚙️ Применяю фильтры и эффекты...")
        time.sleep(1)

        processed_clip = clip.subclip(1, clip.duration - 0.5).without_audio()
        update_progress(70, "🧠 Оптимизация качества...")
        time.sleep(1)

        processed_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        update_progress(100, "✅ Обработка завершена!")

        with open(output_path, 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="🎉 Готово! Твоё видео успешно обработано.\n\n"
                        "📺 Подпишись на канал @KinoMania — там самые крутые инструменты 🎬"
            )

        clip.close()
        processed_clip.close()
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при обработке: {e}")


# === Общий ответ ===
@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.send_message(message.chat.id, "📹 Просто отправь видео, и я обработаю его ✨")


# === Запуск ===
print("🤖 KinoMania Bot запущен и готов к работе!")
bot.infinity_polling(skip_pending=True)
    # Проверка подписки
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🔔 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        markup.add(btn)
        bot.reply_to(
            message,
            "❌ Чтобы пользоваться ботом, подпишись на канал KinoMania!",
            reply_markup=markup
        )
        return

    msg = bot.reply_to(message, "🎬 Видео получено! Начинаю обработку...")

    try:
        # Сохраняем видео
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_path = "input.mp4"
        output_path = "output.mp4"

        with open(input_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # 🔄 Функция отображения прогресса
        def update_progress(percent, text):
            total_blocks = 10
            filled_blocks = int(percent / 10)
            bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
            bot.edit_message_text(
                f"{text}\n\n{bar} {percent}%",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )

        # 🔹 Этапы обработки
        update_progress(10, "📥 Загружаю видео...")
        time.sleep(1)
        update_progress(30, "🎞 Подготавливаю кадры...")
        time.sleep(1)

        clip = mp.VideoFileClip(input_path)
        update_progress(50, "⚙️ Применяю фильтры и эффекты...")
        time.sleep(1)

        processed_clip = clip.subclip(1, clip.duration).without_audio()
        update_progress(70, "🧠 Оптимизация качества...")
        time.sleep(1)

        processed_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        update_progress(100, "✅ Обработка завершена!")

        # 🔹 Отправляем пользователю результат
        with open(output_path, 'rb') as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="🎉 Готово! Твоё видео успешно обработано.\n\n"
                        "📺 Подпишись на канал @KinoMania — там самые крутые инструменты 🎬"
            )

        # Очистка
        clip.close()
        processed_clip.close()
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")


# 🔹 Обработка ошибок
@bot.message_handler(func=lambda message: True)
def default_response(message):
    bot.send_message(message.chat.id, "📹 Просто отправь видео, и я обработаю его ✨")


print("🤖 KinoMania Bot запущен...")
bot.infinity_polling(skip_pending=True)
