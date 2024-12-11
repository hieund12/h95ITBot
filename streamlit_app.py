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
    await update.message.reply_text(
        'Xin chào! Tôi là chatbot chuyên cung cấp kiến thức về mạng, quản trị hệ thống, bảo mật và xử lý sự cố máy tính, máy in, camera. Hãy nhập /flashcard để bắt đầu phiên học flashcard hoặc hỏi bất kỳ điều gì!'
    )

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn trợ giúp"""
    await update.message.reply_text(
        'Hãy nhập bất kỳ câu hỏi nào về mạng, quản trị hệ thống, bảo mật và các chủ đề như Windows Server 2019, Linux, xử lý sự cố máy in, máy tính, camera. Hoặc nhập /flashcard để học liên tục các kiến thức trong 10 phút!'
    )

# Lệnh /flashcard
async def flashcard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Khởi động phiên flashcard"""
    chat_id = update.effective_chat.id

    if chat_id in flashcard_sessions:
        await update.message.reply_text('Bạn đã có một phiên flashcard đang hoạt động. Vui lòng nhập /stop để dừng trước khi bắt đầu phiên mới.')
        return

    flashcard_sessions[chat_id] = True
    await update.message.reply_text('Bắt đầu phiên flashcard! Mỗi 30 giây, tôi sẽ gửi một câu hỏi hoặc kiến thức cho bạn. Phiên sẽ tự động dừng sau 10 phút. Nhập /stop để dừng ngay lập tức.')

    async def send_flashcards():
        """Gửi flashcard mỗi 30 giây trong vòng 10 phút"""
        start_time = time.time()
        while flashcard_sessions.get(chat_id, False):
            if time.time() - start_time > 600:  # Dừng sau 10 phút
                await context.bot.send_message(chat_id=chat_id, text='Phiên flashcard đã kết thúc. Nhập /flashcard để học tiếp.')
                break

            # Sinh câu hỏi từ OpenAI
            question = await generate_flashcard_question()
            await context.bot.send_message(chat_id=chat_id, text=question)
            await asyncio.sleep(30)  # Đợi 30 giây (không chặn event loop)

        flashcard_sessions.pop(chat_id, None)  # Xóa phiên khỏi danh sách

    asyncio.create_task(send_flashcards())

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
        topics = [
            "mạng máy tính", 
            "Windows Server 2019", 
            "quản trị Linux", 
            "lắp ráp máy tính", 
            "xử lý sự cố máy tính", 
            "xử lý sự cố máy in", 
            "xử lý sự cố camera"
        ]
        prompt = f"Tạo một câu hỏi phỏng vấn ngắn về chủ đề ngẫu nhiên từ danh sách: {', '.join(topics)}"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Lỗi khi gọi API OpenAI: {e}")
        return "Không thể tạo câu hỏi flashcard. Vui lòng thử lại sau."

# Khởi chạy bot
def main() -> None:
    """Khởi chạy bot"""
    # Khởi tạo event loop cho thread hiện tại
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Thêm các lệnh /start, /help, /flashcard và /stop
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("flashcard", flashcard_command))
    application.add_handler(CommandHandler("stop", stop_command))

    # Bắt đầu bot
    application.run_polling()

if __name__ == '__main__':
    main()
