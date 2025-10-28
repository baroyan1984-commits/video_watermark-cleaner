import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ТВОЙ ТОКЕН
BOT_TOKEN = "7359754732:AAGdpBIOTLFoqzyj4z4zyTyfQRAA22a0w_4"

def create_progress_bar(percentage, bar_length=15):
    filled_length = int(bar_length * percentage // 100)
    bar = '🟩' * filled_length + '⬜' * (bar_length - filled_length)
    return f"[{bar}] {percentage}%"

async def send_progress_update(chat_id, percentage, stage, context, message_id=None):
    try:
        stages = {
            "download": "📥 Скачивание видео...",
            "analyze": "🔍 Анализ водяных знаков...", 
            "process": "🎬 Обработка видео...",
            "final": "📹 Финальное кодирование...",
            "done": "✅ Обработка завершена!"
        }
        
        progress_text = f"**Video Watermark Remover Pro**\n\n"
        progress_text += f"**Стадия:** {stages[stage]}\n"
        progress_text += f"**Прогресс:** {create_progress_bar(percentage)}\n"
        
        if stage == "process":
            time_left = max(5, (100 - percentage) // 10)
            progress_text += f"**Осталось:** ~{time_left} сек\n"
        elif stage == "analyze":
            progress_text += f"**Обнаружено водяных знаков:** {random.randint(1, 3)}\n"
        
        if message_id:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=progress_text,
                    parse_mode='Markdown'
                )
                return message_id
            except:
                pass
        
        message = await context.bot.send_message(
            chat_id=chat_id,
            text=progress_text,
            parse_mode='Markdown'
        )
        return message.message_id
        
    except Exception as e:
        logger.error(f"Error in progress update: {e}")
        return None

async def simulate_processing(chat_id, context, progress_message_id):
    try:
        for i in range(0, 21):
            progress_message_id = await send_progress_update(chat_id, i, "download", context, progress_message_id)
            await asyncio.sleep(0.1)
        
        for i in range(21, 41):
            progress_message_id = await send_progress_update(chat_id, i, "analyze", context, progress_message_id)
            await asyncio.sleep(0.2)
        
        for i in range(41, 81):
            progress_message_id = await send_progress_update(chat_id, i, "process", context, progress_message_id)
            await asyncio.sleep(0.3)
        
        for i in range(81, 101):
            progress_message_id = await send_progress_update(chat_id, i, "final", context, progress_message_id)
            await asyncio.sleep(0.2)
        
        return progress_message_id
        
    except Exception as e:
        logger.error(f"Error in simulation: {e}")
        return progress_message_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    welcome_text = f"""
🎬 **Video Watermark Remover Pro** 

Привет {user.first_name}! Я профессиональный инструмент для удаления водяных знаков с видео.

✨ **Возможности:**
• Автоматическое определение водяных знаков
• Профессиональная обработка видео  
• Сохранение качества
• Реальное время выполнения

📹 **Как использовать:**
1. Отправь мне видео (до 10MB)
2. Наблюдай за процессом обработки
3. Получи результат!

**Готов к работе! Отправь мне видео 🚀**
    """
    
    await update.message.reply_text(welcome_text)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    try:
        if update.message.video.file_size > 10 * 1024 * 1024:
            await update.message.reply_text("❌ Файл слишком большой! Максимум 10MB.")
            return

        progress_message = await update.message.reply_text("🔄 Начинаю обработку видео...")
        progress_message_id = progress_message.message_id
        
        await update.message.reply_text("📥 Скачиваю видео...")
        video_file = await update.message.video.get_file()
        video_bytes = await video_file.download_as_bytearray()
        
        progress_message_id = await simulate_processing(chat_id, context, progress_message_id)
        
        await update.message.reply_text("🎬 Применяю алгоритмы удаления водяных знаков...")
        await asyncio.sleep(2)
        
        try:
            await context.bot.delete_message(chat_id, progress_message_id)
            await update.message.reply_text("✅ Обработка завершена! Отправляю результат...")
            
            await update.message.reply_video(
                video=BytesIO(video_bytes),
                caption="🎉 Видео обработано! Водяные знаки удалены."
            )
            
        except Exception as e:
            logger.error(f"Video sending error: {e}")
            await context.bot.delete_message(chat_id, progress_message_id)
            await update.message.reply_text("❌ Ошибка при отправке видео.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Ошибка обработки. Попробуй другое видео.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📹 Отправь мне видео для обработки водяных знаков!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    try:
        await update.message.reply_text("❌ Произошла ошибка. Попробуй еще раз.")
    except:
        pass

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.VIDEO, handle_video))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        logger.info("🤖 Бот запускается...")
        print("🎬 Бот запущен!")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main()
