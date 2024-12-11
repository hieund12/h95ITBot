import streamlit as st
import openai
import os
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv  # Đọc API Key từ file .env

# Đọc thông tin từ file .env
load_dotenv()

# Lấy thông tin từ file .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Cấu hình API Key của OpenAI
openai.api_key = OPENAI_API_KEY

# Danh sách các chủ đề cho Flashcard
flashcard_topics = [
    "mạng máy tính", 
    "Windows Server 2019", 
    "quản trị Linux", 
    "lắp ráp máy tính", 
    "xử lý sự cố máy tính", 
    "xử lý sự cố máy in", 
    "xử lý sự cố camera"
]

def generate_flashcard_question(retries=3) -> dict:
    """Gọi API của OpenAI để sinh câu hỏi và câu trả lời flashcard"""
    for attempt in range(retries):
        try:
            topic = random.choice(flashcard_topics)
            prompt = f"Tạo một câu hỏi và câu trả lời rõ ràng, cụ thể, dễ hiểu về chủ đề {topic}. Định dạng: 'Câu hỏi: [Nội dung câu hỏi] Trả lời: [Nội dung câu trả lời]'."
            
            response = openai.ChatCompletion.create(
                model="gpt-4", 
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message['content']
            # Phân tách câu hỏi và câu trả lời
            question, answer = content.split("Trả lời:", 1) if "Trả lời:" in content else (content, "Không có câu trả lời.")
            return {"question": question.strip(), "answer": answer.strip()}
        except Exception as e:
            st.warning(f"⚠️ Lỗi khi tạo flashcard (thử lần {attempt + 1} / {retries}): {e}")
            time.sleep(2)  # Đợi 2 giây trước khi thử lại
    return {"question": "❌ Không thể tạo câu hỏi flashcard.", "answer": "Vui lòng thử lại sau."}

def display_flashcard(flashcard: dict, card_number: int, total_cards: int) -> None:
    """Hiển thị flashcard trên giao diện Streamlit"""
    st.markdown(f"""
    <div style="border-radius: 10px; background-color: #f5f5f5; padding: 20px; text-align: left; font-size: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); margin-bottom: 20px;">
        <strong>Flashcard {card_number}/{total_cards}</strong>
        <p><strong>Câu hỏi:</strong> {flashcard['question']}</p>
        <p><strong>Trả lời:</strong> {flashcard['answer']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Giao diện chính của Streamlit"""
    st.title('📚 Flashcard Learning App (Slide View)')
    st.markdown('**💪 Mỗi 20 giây sẽ có 1 flashcard mới trong vòng 10 phút.**')
    st.write('🎉 Nhấn **Start Learning** để bắt đầu học. Flashcard sẽ tự động chuyển đổi sau 20 giây.')

    # Khởi tạo session state
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = None

    if 'flashcard_count' not in st.session_state:
        st.session_state['flashcard_count'] = 0

    if 'daily_flashcard_limit' not in st.session_state:
        st.session_state['daily_flashcard_limit'] = 20

    if 'flashcard_text' not in st.session_state:
        st.session_state['flashcard_text'] = generate_flashcard_question()

    if 'next_available_time' not in st.session_state:
        st.session_state['next_available_time'] = None

    if st.session_state['next_available_time'] and datetime.now() < st.session_state['next_available_time']:
        time_left = st.session_state['next_available_time'] - datetime.now()
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        st.warning(f"⏳ Vui lòng quay lại sau {hours} giờ {minutes} phút để tiếp tục học.")
    else:
        if st.button('🎉 Start Learning'):
            st.session_state['start_time'] = time.time()
            st.session_state['flashcard_count'] = 0
            st.session_state['flashcard_text'] = generate_flashcard_question()

        if st.session_state['start_time'] is not None:
            time_elapsed = time.time() - st.session_state['start_time']
            remaining_time = max(0, 600 - int(time_elapsed))  # 10 phút = 600 giây
            minutes, seconds = divmod(remaining_time, 60)
            
            st.write(f'⏰ **Thời gian còn lại: {minutes} phút {seconds} giây**')

            if remaining_time == 0:
                st.success('🎉 **Hết thời gian học! Nhấn "Start Learning" để bắt đầu phiên học mới.**')
                st.session_state['start_time'] = None
            else:
                current_flashcard = st.session_state['flashcard_count'] + 1

                if current_flashcard <= st.session_state['daily_flashcard_limit']:
                    display_flashcard(st.session_state['flashcard_text'], current_flashcard, st.session_state['daily_flashcard_limit'])

                    countdown = 20 - (int(time.time() - st.session_state['start_time']) % 20)
                    st.write(f'🕒 **Chuyển flashcard tiếp theo sau: {countdown} giây**')

                    if countdown == 0:
                        st.session_state['flashcard_count'] += 1
                        if st.session_state['flashcard_count'] < st.session_state['daily_flashcard_limit']:
                            st.session_state['flashcard_text'] = generate_flashcard_question()
                            st.experimental_rerun()
                        else:
                            st.success('✨ **Bạn đã hoàn thành tất cả các flashcard!** ✨')
                            st.session_state['start_time'] = None
                            st.session_state['next_available_time'] = datetime.now() + timedelta(hours=12)
                            st.experimental_rerun()
                else:
                    st.success('✨ **Bạn đã hoàn thành tất cả các flashcard cho hôm nay!** ✨')
                    st.session_state['start_time'] = None
                    st.session_state['next_available_time'] = datetime.now() + timedelta(hours=12)

if __name__ == '__main__':
    main()
