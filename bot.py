# (в начале файла уже должны быть импорты)
import os
import subprocess
import time
import telebot
from telebot import types
# ... остальной код и настройки (BOT_TOKEN и пр.)

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ВАШ_ТОКЕН_ЗДЕСЬ"
if not BOT_TOKEN:
    raise SystemExit("ERROR: BOT_TOKEN env var not set")

bot = telebot.TeleBot(BOT_TOKEN)
CHANNEL_INVITE_LINK = "https://t.me/Franglon"  # твоя приглашалка

# --- Функция для обновления статуса (отправка/редактирование сообщений) ---
def set_progress_message(chat_id, msg_id, text):
    try:
        bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id)
    except Exception:
        try:
            bot.send_message(chat_id, text)
        except Exception:
            pass

# --- Обработка видео с blur внизу ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # проверка подписки (если нужна) — убери или оставь
    # if not is_subscribed(user_id): ... (ваша логика)

    info_msg = bot.reply_to(message, "🎬 Видео получено — начинаю обработку (blur)...\n0%")
    try:
        file_info = bot.get_file(message.video.file_id)
        downloaded = bot.download_file(file_info.file_path)

        input_path = f"/tmp/input_{user_id}.mp4"
        output_path = f"/tmp/output_{user_id}.mp4"

        with open(input_path, "wb") as f:
            f.write(downloaded)

        # 1) статус
        set_progress_message(chat_id, info_msg.message_id, "🎬 Видео загружено — 10%")

        # 2) FFmpeg команда: размытие нижней области (12% высоты). Подстрой при необходимости.
        # filter: split video, crop bottom 12% -> boxblur -> overlay обратно
        blur_height = 0.12  # 0.12 = 12% высоты; если нужно больше — поставить 0.15 и т.д.
        boxblur_radius = 20  # чем больше — тем сильнее размытие

        vf = (
            f"split=2[a][b];"
            f"[a]crop=in_w:in_h*{blur_height}:0:in_h*(1-{blur_height}),boxblur={boxblur_radius}[blurred];"
            f"[b][blurred]overlay=0:in_h*(1-{blur_height})"
        )

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            output_path
        ]

        set_progress_message(chat_id, info_msg.message_id, "⚙️ Применяю размытие — 30%")
        # запустить ffmpeg (блокирующий вызов)
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if proc.returncode != 0:
            # лог для дебага
            err = proc.stderr[:2000]
            bot.send_message(chat_id, f"❌ FFmpeg ошибку вернул:\n{err}")
            raise RuntimeError("FFmpeg failed")

        set_progress_message(chat_id, info_msg.message_id, "🔧 Финальная обработка — 60%")
        time.sleep(0.5)
        set_progress_message(chat_id, info_msg.message_id, "📦 Подготовка результата — 90%")
        time.sleep(0.5)

        # Отправляем видео обратно
        with open(output_path, "rb") as out_vid:
            bot.send_video(chat_id, out_vid, caption="✅ Готово — зона логотипа размыта (blur).")

        set_progress_message(chat_id, info_msg.message_id, "✅ Завершено — 100%")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка при обработке: {e}")
    finally:
        # Очистка временных файлов
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass
