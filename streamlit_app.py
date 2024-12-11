import streamlit as st
import openai
import os
import time
import random
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

def generate_flashcard_question() -> str:
    """Gọi API của OpenAI để sinh câu hỏi flashcard"""
    try:
        topic = random.choice(flashcard_topics)
        prompt = f"Tạo một câu hỏi ngắn, thân thiện và dễ hiểu về chủ đề {topic}. Định dạng: Câu hỏi ngắn + câu trả lời đầy đủ."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return "Không thể tạo câu hỏi flashcard. Vui lòng thử lại sau."

def display_flashcard(flashcard: str, card_number: int, total_cards: int) -> None:
    """Hiển thị flashcard trên giao diện Streamlit"""
    st.markdown(f"""
    <div style="
        border-radius: 10px;
        background-color: #f5f5f5;
        padding: 20px;
        text-align: center;
        font-size: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 20px;">
        <strong>Flashcard {card_number}/{total_cards}</strong>
        <p>{flashcard}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Giao diện chính của Streamlit"""
    st.title('📚 Flashcard Learning App')
    st.markdown('**💪 Mỗi 30 giây sẽ có 1 flashcard mới trong vòng 10 phút.**')
    st.write('🎉 Nhấn **Start Learning** để bắt đầu học. Mỗi flashcard sẽ hiển thị tự động.')

    # Khởi tạo session state
    if 'start_time' not in st.session_state:
        st.session_state['start_time'] = None

    if 'flashcard_count' not in st.session_state:
        st.session_state['flashcard_count'] = 0

    if 'total_flashcards' not in st.session_state:
        st.session_state['total_flashcards'] = 20  # Tổng số flashcard trong 10 phút (10 phút, mỗi 30 giây 1 flashcard)

    if 'flashcard_text' not in st.session_state:
        st.session_state['flashcard_text'] = generate_flashcard_question()

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

            if current_flashcard <= st.session_state['total_flashcards']:
                display_flashcard(st.session_state['flashcard_text'], current_flashcard, st.session_state['total_flashcards'])

                if st.button('✅ OK', key=f'ok_button_{current_flashcard}'):
                    st.session_state['flashcard_count'] += 1
                    if st.session_state['flashcard_count'] < st.session_state['total_flashcards']:
                        st.session_state['flashcard_text'] = generate_flashcard_question()
                    else:
                        st.success('✨ **Bạn đã hoàn thành tất cả các flashcard!** ✨')
                        st.session_state['start_time'] = None
            else:
                st.success('✨ **Bạn đã hoàn thành tất cả các flashcard!** ✨')
                st.session_state['start_time'] = None

if __name__ == '__main__':
    main()
