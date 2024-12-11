import logging
import openai
import os
import time
import threading
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import streamlit as st

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

# Biến toàn cục để điều khiển phiên flashcard và interview
flashcard_sessions = {}
interview_sessions = {}

# Khởi tạo bot và application
app = Flask(__name__)
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn chào mừng khi người dùng nhập /start"""
    await update.message.reply_text('Xin chào! Tôi là chatbot chuyên cung cấp kiến thức về mạng, quản trị hệ thống và bảo mật. Hãy nhập /flashcard hoặc /interview để học tập hoặc luyện phỏng vấn!')

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn trợ giúp"""
    await update.message.reply_text('Hãy nhập /flashcard để học flashcard hoặc /interview để luyện tập phỏng vấn. Nhập /stop để dừng các phiên hiện tại.')

# Lệnh /flashcard
async def flashcard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Khởi động phiên flashcard"""
    chat_id = update.effective_chat.id

    if chat_id in flashcard_sessions:
        await update.message.reply_text('Bạn đã có một phiên flashcard đang hoạt động. Vui lòng nhập /stop để dừng trước khi bắt đầu phiên mới.')
        return

    flashcard_sessions[chat_id] = True
    await update.message.reply_text('Bắt đầu phiên flashcard! Mỗi 30 giây, tôi sẽ gửi một câu hỏi hoặc kiến thức cho bạn. Phiên sẽ tự động dừng sau 10 phút. Nhập /stop để dừng ngay lập tức.')

    def send_flashcards():
        start_time = time.time()
        while flashcard_sessions.get(chat_id, False):
            if time.time() - start_time > 600:  # Dừng sau 10 phút
                application.bot.send_message(chat_id=chat_id, text='Phiên flashcard đã kết thúc. Nhập /flashcard để học tiếp.')
                break

            question = generate_flashcard_question()
            application.bot.send_message(chat_id=chat_id, text=question)
            time.sleep(30)

        flashcard_sessions.pop(chat_id, None)

    threading.Thread(target=send_flashcards).start()

# Lệnh /interview
async def interview_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Khởi động phiên interview"""
    chat_id = update.effective_chat.id

    if chat_id in interview_sessions:
        await update.message.reply_text('Bạn đã có một phiên interview đang hoạt động. Vui lòng nhập /stop để dừng trước khi bắt đầu phiên mới.')
        return

    interview_sessions[chat_id] = True
    await update.message.reply_text('Bắt đầu phiên phỏng vấn! Mỗi 30 giây, tôi sẽ gửi một câu hỏi phỏng vấn cho bạn. Phiên sẽ tự động dừng sau 10 phút. Nhập /stop để dừng ngay lập tức.')

    def send_interview_questions():
        start_time = time.time()
        while interview_sessions.get(chat_id, False):
            if time.time() - start_time > 600:
                application.bot.send_message(chat_id=chat_id, text='Phiên phỏng vấn đã kết thúc. Nhập /interview để luyện tiếp.')
                break

            question = generate_interview_question()
            application.bot.send_message(chat_id=chat_id, text=question)
            time.sleep(30)

        interview_sessions.pop(chat_id, None)

    threading.Thread(target=send_interview_questions).start()

# Lệnh /stop
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    flashcard_sessions[chat_id] = False
    interview_sessions[chat_id] = False
    await update.message.reply_text('Các phiên hiện tại đã dừng.')

# Gọi API ChatGPT để sinh câu hỏi flashcard
def generate_flashcard_question():
    prompt = "Tạo một câu hỏi flashcard về mạng, Linux, máy in hoặc camera."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Gọi API ChatGPT để sinh câu hỏi phỏng vấn
def generate_interview_question():
    prompt = "Tạo một câu hỏi phỏng vấn IT Helpdesk hoặc quản trị hệ thống (0-1 năm kinh nghiệm)."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Thêm các lệnh vào bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("flashcard", flashcard_command))
application.add_handler(CommandHandler("interview", interview_command))
application.add_handler(CommandHandler("stop", stop_command))

# Chạy Flask và Streamlit song song
def run_flask():
    app.run(host='0.0.0.0', port=8443)

def run_streamlit():
    st.title('Telegram Bot Controller')
    st.write('Sử dụng bot để nhận câu hỏi phỏng vấn và flashcard trực tiếp từ Telegram.')

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    threading.Thread(target=application.run_polling).start()
    run_streamlit()
