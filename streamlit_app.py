import logging
import openai
import os
import time
import asyncio  # Import asyncio để tạo event loop thủ công
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv  # Đọc API Key từ file .env

# Đọc thông tin từ file .env
load_dotenv()

# Lấy thông tin từ file .env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Kiểm tra token Telegram
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN không được tìm thấy trong file .env hoặc bị trống. Kiểm tra lại.")

# Cấu hình API Key của OpenAI
openai.api_key = OPENAI_API_KEY

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Biến toàn cục để điều khiển phiên flashcard
flashcard_sessions = {}

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn chào mừng khi người dùng nhập /start"""
    await update.message.reply_text('Xin chào! Tôi là chatbot hỗ trợ học tập.')

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn trợ giúp"""
    await update.message.reply_text('Bạn có thể nhập /flashcard để bắt đầu học flashcard.')

# Lệnh /flashcard
async def flashcard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Khởi động phiên flashcard"""
    chat_id = update.effective_chat.id
    flashcard_sessions[chat_id] = True
    await update.message.reply_text('Bắt đầu phiên flashcard! Mỗi 30 giây, tôi sẽ gửi một câu hỏi cho bạn. Nhập /stop để dừng.')

# Lệnh /stop
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dừng phiên flashcard hiện tại"""
    chat_id = update.effective_chat.id
    if chat_id in flashcard_sessions:
        flashcard_sessions[chat_id] = False
        await update.message.reply_text('Phiên flashcard đã dừng. Nhập /flashcard để bắt đầu phiên mới.')
    else:
        await update.message.reply_text('Hiện không có phiên flashcard nào đang chạy.')

# Gọi API ChatGPT để sinh câu hỏi ngẫu nhiên cho flashcard
async def generate_flashcard_question() -> str:
    """Gọi API của OpenAI để sinh câu hỏi flashcard"""
    try:
        prompt = "Tạo một câu hỏi phỏng vấn ngắn về chủ đề mạng máy tính."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Lỗi khi gọi API OpenAI: {e}")
        return "Không thể tạo câu hỏi flashcard. Vui lòng thử lại sau."

# Khởi chạy bot
async def run_application():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Thêm các lệnh /start, /help, /flashcard và /stop
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flashcard", flashcard_command))
    application.add_handler(CommandHandler("stop", stop_command))

    # Thay vì run_polling(), sử dụng start_polling() và giữ vòng lặp hoạt động
    await application.start_polling()
    try:
        # Giữ bot hoạt động trong 3600 giây (1 giờ)
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logging.info("Dừng bot...")
    finally:
        await application.stop()

def main() -> None:
    """Chạy ứng dụng asyncio trong luồng chính"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_application())

if __name__ == '__main__':
    main()
