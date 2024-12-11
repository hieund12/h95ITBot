import logging
import openai
import os
import time
import threading
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Đọc API Key từ file .env
from dotenv import load_dotenv
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
def start(update: Update, context: CallbackContext) -> None:
    """Gửi tin nhắn chào mừng khi người dùng nhập /start"""
    update.message.reply_text('Xin chào! Tôi là chatbot chuyên cung cấp kiến thức về mạng, quản trị hệ thống, bảo mật và xử lý sự cố máy tính, máy in, camera. Hãy nhập /flashcard để bắt đầu phiên học flashcard hoặc hỏi bất kỳ điều gì!')

# Lệnh /help
def help_command(update: Update, context: CallbackContext) -> None:
    """Gửi tin nhắn trợ giúp"""
    update.message.reply_text('Hãy nhập bất kỳ câu hỏi nào về mạng, quản trị hệ thống, bảo mật và các chủ đề như Windows Server 2019, Linux, xử lý sự cố máy in, máy tính, camera. Hoặc nhập /flashcard để học liên tục các kiến thức trong 10 phút!')

# Lệnh /flashcard
def flashcard_command(update: Update, context: CallbackContext) -> None:
    """Khởi động phiên flashcard"""
    chat_id = update.effective_chat.id

    if chat_id in flashcard_sessions:
        update.message.reply_text('Bạn đã có một phiên flashcard đang hoạt động. Vui lòng nhập /stop để dừng trước khi bắt đầu phiên mới.')
        return

    flashcard_sessions[chat_id] = True
    update.message.reply_text('Bắt đầu phiên flashcard! Mỗi 30 giây, tôi sẽ gửi một câu hỏi hoặc kiến thức cho bạn. Phiên sẽ tự động dừng sau 10 phút. Nhập /stop để dừng ngay lập tức.')

    def send_flashcards():
        """Gửi flashcard mỗi 30 giây trong vòng 10 phút"""
        start_time = time.time()
        while flashcard_sessions.get(chat_id, False):
            if time.time() - start_time > 600:  # Dừng sau 10 phút
                update.message.reply_text('Phiên flashcard đã kết thúc. Nhập /flashcard để học tiếp.')
                break

            # Sinh câu hỏi từ OpenAI
            question = generate_flashcard_question()
            context.bot.send_message(chat_id=chat_id, text=question)
            time.sleep(30)  # Đợi 30 giây

        flashcard_sessions.pop(chat_id, None)  # Xóa phiên khỏi danh sách

    threading.Thread(target=send_flashcards).start()

# Lệnh /stop
def stop_command(update: Update, context: CallbackContext) -> None:
    """Dừng phiên flashcard hiện tại"""
    chat_id = update.effective_chat.id
    if chat_id in flashcard_sessions:
        flashcard_sessions[chat_id] = False
        update.message.reply_text('Phiên flashcard đã dừng. Nhập /flashcard để bắt đầu phiên mới.')
    else:
        update.message.reply_text('Hiện không có phiên flashcard nào đang chạy.')

# Gọi API ChatGPT để sinh câu hỏi ngẫu nhiên cho flashcard
def generate_flashcard_question():
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
            messages=[{"role": "system", "content": "Bạn là AI chuyên tạo các câu hỏi phỏng vấn ngắn về các chủ đề công nghệ."}, 
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Lỗi khi gọi API OpenAI: {e}")
        return "Không thể tạo câu hỏi flashcard. Vui lòng thử lại sau."

# Khởi chạy bot
def main() -> None:
    """Khởi chạy bot"""
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    # Thêm các lệnh /start, /help, /flashcard và /stop
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("flashcard", flashcard_command))
    dispatcher.add_handler(CommandHandler("stop", stop_command))

    # Bắt đầu bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
