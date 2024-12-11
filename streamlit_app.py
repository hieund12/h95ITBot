import streamlit as st
import openai
import os
import time
import random
from dotenv import load_dotenv

# Đọc thông tin từ file .env
load_dotenv()

# Lấy thông tin từ file .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Kiểm tra API Key
if not OPENAI_API_KEY:
    st.error('❌ API Key không tìm thấy. Vui lòng kiểm tra file .env và chắc chắn rằng bạn đã thêm OPENAI_API_KEY')

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

def generate_flashcard_question(retries=3) -> str:
    """Gọi API của OpenAI để sinh câu hỏi flashcard"""
    for attempt in range(retries):
        try:
            topic = random.choice(flashcard_topics)
            prompt = f"Tạo một câu hỏi ngắn và một câu trả lời đầy đủ. Chủ đề: {topic}. Định dạng: Câu hỏi: [nội dung] Câu trả lời: [nội dung]."
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Bạn là AI chuyên tạo flashcard học tập ngắn gọn, đầy đủ, kết thúc tự nhiên và dễ hiểu."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150, 
                temperature=0.5, 
                stop=["\n\n"] 
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            st.warning(f"⚠️ Lỗi khi tạo flashcard (thử lần {attempt + 1} / {retries}): {e}")
            time.sleep(2)
    return "❌ Không thể tạo câu hỏi flashcard sau nhiều lần thử. Vui lòng thử lại sau."

def split_question_answer(flashcard_text: str) -> tuple:
    """Tách phần câu hỏi và câu trả lời từ nội dung trả về của OpenAI."""
    if "Câu hỏi:" in flashcard_text and "Câu trả lời:" in flashcard_text:
        question = flashcard_text.split("Câu hỏi:")[1].split("Câu trả lời:")[0].strip()
        answer = flashcard_text.split("Câu trả lời:")[1].strip()
    else:
        parts = flashcard_text.split('. ', 1)
        question = parts[0] if len(parts) > 0 else "Không thể tách câu hỏi"
        answer = parts[1] if len(parts) > 1 else "Không thể tách câu trả lời"
    return question, answer

def display_flashcard(question: str, answer: str, card_number: int, total_cards: int) -> None:
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
        <hr style="border: none; border-top: 2px solid #ccc; margin: 10px 0;">
        <strong>Câu hỏi:</strong>
        <p style="color: #333; font-weight: bold;">{question}</p>
        <hr style="border: none; border-top: 2px dashed #ccc; margin: 10px 0;">
        <strong>Câu trả lời:</strong>
        <p style="color: #555;">{answer}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title('📚 Flashcard Learning App')
    st.markdown('**💪 Mỗi 30 giây sẽ có 1 flashcard mới trong vòng 10 phút.**')
    st.write('🎉 Nhấn **Start Learning** để bắt đầu học.')

    if st.button('🎉 Start Learning'):
        for i in range(1, 21):
            flashcard_text = generate_flashcard_question()
            question, answer = split_question_answer(flashcard_text)
            display_flashcard(question, answer, i, 20)
            if st.button('✅ OK', key=f'ok_button_{i}'):
                continue
            time.sleep(30)
        st.success('✨ **Bạn đã hoàn thành tất cả các flashcard!** ✨')

if __name__ == '__main__':
    main()
