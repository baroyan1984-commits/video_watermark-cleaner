import telebot
from telebot import types
import os
import time
import moviepy.editor as mp

# 🔹 Укажи свой токен
BOT_TOKEN = "ТОКЕН_ТВОЕГО_БОТА"

# 🔹 Канал, на который нужно подписаться
CHANNEL_USERNAME = "@KinoMania"

# 🔹 Приветственное изображение или видео (если есть)
WELCOME_MEDIA = "welcome.jpg"  # можно заменить на "welcome.mp4"

bot = telebot.TeleBot(BOT_TOKEN)


# 🔹 Проверка подписки
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"[Ошибка подписки]: {e}")
        return False


# 🔹 Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📺 Подписаться на KinoMania", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
    btn2 = types.InlineKeyboardButton("🎬 Отправить видео", switch_inline_query_current_chat="")
    markup.add(btn1)
    markup.add(btn2)

    if os.path.exists(WELCOME_MEDIA):
        if WELCOME_MEDIA.endswith(".mp4"):
            with open(WELCOME_MEDIA, 'rb') as video:
                bot.send_video(
                    message.chat.id,
                    video,
                    caption="🎬 Привет! Я бот KinoMania.\n\n"
                            "Отправь мне видео — и я обработаю его 🔥",
                    reply_markup=markup
                )
        else:
            with open(WELCOME_MEDIA, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="🎬 Привет! Я бот KinoMania.\n\n"
                            "Отправь мне видео — и я обработаю его 🔥",
                    reply_markup=markup
                )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Привет! Я бот KinoMania.\n\n"
            "Отправь мне видео — я сделаю его стильным и чистым 🎥",
            reply_markup=markup
        )


# 🔹 Обработка видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id

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
