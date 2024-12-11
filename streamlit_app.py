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
    await update.message.reply_text('Xin chào! Tôi là chatbot chuyên cung cấp kiến thức về mạng, quản trị hệ thống và bảo mật.')

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Nhập /flashcard để học flashcard hoặc /interview để luyện tập phỏng vấn. Nhập /stop để dừng.')

# Lệnh /flashcard
async def flashcard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    flashcard_sessions[chat_id] = True
    await update.message.reply_text('Bắt đầu phiên flashcard!')

# Lệnh /stop
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    flashcard_sessions[chat_id] = False
    await update.message.reply_text('Các phiên hiện tại đã dừng.')

# Gọi API ChatGPT để sinh câu hỏi flashcard
def generate_flashcard_question():
    prompt = "Tạo một câu hỏi flashcard về mạng."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Thêm các lệnh vào bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("flashcard", flashcard_command))
application.add_handler(CommandHandler("stop", stop_command))

# Webhook của Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'ok'

# Chạy Flask và Streamlit song song
def run_flask():
    PORT = int(os.getenv('PORT', '5000'))  # Đổi cổng thành 5000
    app.run(host='0.0.0.0', port=PORT)

def run_streamlit():
    st.title('Telegram Bot Controller')
    st.write('Sử dụng bot để nhận câu hỏi phỏng vấn và flashcard trực tiếp từ Telegram.')

def run_telegram_bot():
    asyncio.run(application.run_polling())

if __name__ == '__main__':
    # Chạy Flask trên cổng 5000 và Streamlit trên cổng 8501
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_telegram_bot).start()
    run_streamlit()
