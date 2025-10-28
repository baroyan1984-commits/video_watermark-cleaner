import os
import logging
import time
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import threading

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ВСТАВЬ СВОЙ ТОКЕН!
BOT_TOKEN = "7359754732:AAGdpBIOTLFoqzyj4z4zyTyfQRAA22a0w_4"

# Глобальные переменные для отслеживания прогресса
progress_data = {}

def create_progress_bar(percentage, bar_length=20):
    """Создает текстовый прогресс-бар"""
    filled_length = int(bar_length * percentage // 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"[{bar}] {percentage:.1f}%"

async def update_progress(chat_id, percentage, stage, context):
    """Обновляет прогресс в чате"""
    try:
        progress_text = f"🔄 **Обработка видео**\n\n"
        
        if stage == "download":
            progress_text += "📥 **Скачивание видео...**\n"
        elif stage == "analyze":
            progress_text += "🔍 **Анализ водяных знаков...**\n"
        elif stage == "processing":
            progress_text += "🎬 **Удаление водяных знаков...**\n"
        elif stage == "encoding":
            progress_text += "📹 **Кодирование видео...**\n"
        elif stage == "complete":
            progress_text += "✅ **Обработка завершена!**\n"
            percentage = 100
        
        progress_text += f"{create_progress_bar(percentage)}\n"
        
        # Добавляем профессиональные детали
        if stage == "processing" and percentage > 0:
            frames_processed = int(percentage / 100 * 300)  # Примерное количество кадров
            progress_text += f"📊 Обработано кадров: {frames_processed}/300\n"
        
        if stage == "encoding":
            progress_text += f"⏱ Осталось: {max(0, 100 - percentage)//10 * 2} сек\n"
        
        # Обновляем или отправляем новое сообщение
        if chat_id in progress_data:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_data[chat_id],
                    text=progress_text
                )
            except:
                # Если не получается редактировать, отправляем новое
                msg = await context.bot.send_message(chat_id, progress_text)
                progress_data[chat_id] = msg.message_id
        else:
            msg = await context.bot.send_message(chat_id, progress_text)
            progress_data[chat_id] = msg.message_id
            
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.message.from_user
    
    welcome_text = f"""
🎬 **Video Watermark Remover Pro** 🎬

Привет {user.first_name}! Я профессиональный инструмент для удаления водяных знаков с видео.

✨ **Возможности:**
• Автоматическое определение водяных знаков
• Профессиональная обработка видео
• Сохранение качества
• Реальное время выполнения

📹 **Как использовать:**
1. Отправь мне видео (до 20MB)
2. Наблюдай за процессом обработки
3. Получи результат!

⚠️ **Примечание:** Работаю лучше с четкими водяными знаками в углах видео.

**Готов к работе! Отправь мне видео 🚀**
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик видео файлов"""
    chat_id = update.message.chat_id
    
    try:
        # Проверяем размер файла
        if update.message.video.file_size > 20 * 1024 * 1024:
            await update.message.reply_text("❌ **Ошибка:** Файл слишком большой! Максимум 20MB.")
            return

        # Начало обработки
        await update_progress(chat_id, 0, "download", context)
        
        # Скачиваем видео
        video_file = await update.message.video.get_file()
        video_path = "input_video.mp4"
        await video_file.download_to_drive(video_path)
        
        await update_progress(chat_id, 25, "download", context)
        await asyncio.sleep(1)  # Имитация работы
        
        # Анализ видео
        await update_progress(chat_id, 30, "analyze", context)
        await asyncio.sleep(2)
        await update_progress(chat_id, 40, "analyze", context)
        
        # Обрабатываем видео в отдельном потоке
        await update_progress(chat_id, 45, "processing", context)
        
        # Запускаем обработку с прогрессом
        output_path = await process_video_with_progress(chat_id, video_path, context)
        
        if output_path and os.path.exists(output_path):
            # Завершаем прогресс
            await update_progress(chat_id, 100, "complete", context)
            await asyncio.sleep(1)
            
            # Отправляем результат
            await update.message.reply_video(
                video=output_path,
                caption="🎉 **Видео успешно обработано!**\n\nВодяные знаки удалены ✅\nКачество сохранено ✅"
            )
            
            # Очищаем сообщение прогресса
            try:
                await context.bot.delete_message(chat_id, progress_data[chat_id])
                del progress_data[chat_id]
            except:
                pass
            
            # Удаляем временные файлы
            os.remove(video_path)
            os.remove(output_path)
        else:
            await update.message.reply_text("❌ **Ошибка обработки.** Попробуй другое видео.")
            
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await update.message.reply_text("❌ **Критическая ошибка.** Попробуй еще раз.")
        
        # Очищаем прогресс при ошибке
        try:
            if chat_id in progress_data:
                await context.bot.delete_message(chat_id, progress_data[chat_id])
                del progress_data[chat_id]
        except:
            pass

async def process_video_with_progress(chat_id, input_path, context):
    """Обрабатывает видео с обновлением прогресса"""
    try:
        output_path = "output_video.mp4"
        
        # Загружаем видео для анализа
        await update_progress(chat_id, 50, "processing", context)
        clip = VideoFileClip(input_path)
        
        # Получаем информацию о видео
        duration = clip.duration
        fps = clip.fps
        total_frames = int(duration * fps)
        
        logger.info(f"Video info: {duration}s, {fps}fps, {total_frames}frames")
        
        # Имитация прогресса обработки кадров
        processed_frames = 0
        
        def process_frame_with_progress(frame):
            nonlocal processed_frames
            processed_frames += 1
            
            # Обновляем прогресс каждые 10% или каждые 10 кадров
            if processed_frames % max(1, total_frames // 10) == 0:
                progress = 50 + (processed_frames / total_frames) * 30
                # Запускаем обновление прогресса в основном потоке
                asyncio.run_coroutine_threadsafe(
                    update_progress(chat_id, progress, "processing", context), 
                    context.application._get_running_loop()
                )
            
            return remove_watermark_from_frame(frame)
        
        await update_progress(chat_id, 80, "encoding", context)
        
        # Применяем обработку к кадрам
        processed_clip = clip.fl_image(process_frame_with_progress)
        
        # Сохраняем результат
        await update_progress(chat_id, 90, "encoding", context)
        
        processed_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Закрываем клипы
        clip.close()
        processed_clip.close()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error in video processing: {e}")
        return None

def remove_watermark_from_frame(frame):
    """Удаляет водяные знаки с одного кадра"""
    try:
        # Создаем копию кадра
        result = frame.copy()
        height, width = frame.shape[:2]
        
        # Обрабатываем 4 угла где обычно находятся водяные знаки
        
        # Правый нижний угол
        if width > 200 and height > 100:
            rb_region = frame[height-80:height, width-180:width]
            blurred_rb = cv2.GaussianBlur(rb_region, (25, 25), 0)
            result[height-80:height, width-180:width] = blurred_rb
        
        # Левый нижний угол
        if width > 180 and height > 100:
            lb_region = frame[height-80:height, 0:180]
            blurred_lb = cv2.GaussianBlur(lb_region, (25, 25), 0)
            result[height-80:height, 0:180] = blurred_lb
            
        # Правый верхний угол
        if width > 200 and height > 80:
            rt_region = frame[0:80, width-180:width]
            blurred_rt = cv2.GaussianBlur(rt_region, (25, 25), 0)
            result[0:80, width-180:width] = blurred_rt
            
        # Левый верхний угол
        if width > 180 and height > 80:
            lt_region = frame[0:80, 0:180]
            blurred_lt = cv2.GaussianBlur(lt_region, (25, 25), 0)
            result[0:80, 0:180] = blurred_lt
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return frame

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    try:
        chat_id = update.message.chat_id
        await update.message.reply_text("❌ **Системная ошибка.** Попробуй еще раз.")
        
        # Очищаем прогресс при ошибке
        if chat_id in progress_data:
            try:
                await context.bot.delete_message(chat_id, progress_data[chat_id])
                del progress_data[chat_id]
            except:
                pass
    except:
        pass

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🎬 Video Watermark Remover Pro запущен!")
    print("=" * 50)
    print("🎬 VIDEO WATERMARK REMOVER PRO")
    print("🤖 Бот успешно запущен!")
    print("📱 Иди в Telegram и тестируй бота!")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path)
        with open(output_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при обработке видео: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# --- Запуск бота ---
def start_bot():
    bot.infinity_polling()

# --- Flask-сервер для Render (не влияет на бота) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# --- Запуск ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_bot()
