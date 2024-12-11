import streamlit as st
import openai
import os
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

def generate_flashcard_question(retries=3) -> dict:
    """Gọi API của OpenAI để sinh câu hỏi và câu trả lời flashcard"""
    for attempt in range(retries):
        try:
            topic = random.choice(flashcard_topics)
            prompt = f"Tạo một câu hỏi và câu trả lời rõ ràng, cụ thể, dễ hiểu về chủ đề {topic}. Định dạng: 'Câu hỏi: [Nội dung câu hỏi] Trả lời: [Nội dung câu trả lời]'"
            
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
    return {"question": "❌ Không thể tạo câu hỏi flashcard.", "answer": "Vui lòng thử lại sau."}

def display_flashcard(flashcard: dict, card_number: int, total_cards: int) -> None:
    """Hiển thị flashcard trên giao diện Streamlit"""
    st.markdown(f"""
    <div style="border-radius: 10px; background-color: #f5f5f5; padding: 20px; text-align: left; font-size: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); margin-bottom: 20px;">
        <strong>Flashcard {card_number}/{total_cards}</strong>
        <p><strong>🟡 Câu hỏi:</strong> {flashcard['question']}</p>
        <p><strong>🟢 Trả lời:</strong> {flashcard['answer']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Giao diện chính của Streamlit"""
    st.title('📚 Flashcard Learning App (Slide View)')
    st.markdown('**💪 Học với 10 flashcards mỗi lần. Nhấn "Start Learning" để bắt đầu học.**')
    st.write('🎉 Nhấn **Start Learning** để bắt đầu học. Nhấn **Next** để chuyển sang flashcard tiếp theo.')

    # Khởi tạo session state
    if 'flashcard_list' not in st.session_state:
        st.session_state['flashcard_list'] = []

    if 'flashcard_count' not in st.session_state:
        st.session_state['flashcard_count'] = 0

    if st.button('🎉 Start Learning'):
        st.session_state['flashcard_count'] = 0
        st.session_state['flashcard_list'] = [generate_flashcard_question() for _ in range(10)]  # Giới hạn 10 flashcards mỗi lần

    if st.session_state['flashcard_count'] < len(st.session_state['flashcard_list']):
        current_flashcard = st.session_state['flashcard_count'] + 1
        flashcard = st.session_state['flashcard_list'][st.session_state['flashcard_count']]
        display_flashcard(flashcard, current_flashcard, len(st.session_state['flashcard_list']))

        if st.button('⏭️ Next', key=f'next_button_{current_flashcard}'):
            st.session_state['flashcard_count'] += 1

            if st.session_state['flashcard_count'] >= len(st.session_state['flashcard_list']):
                st.success('✨ **Bạn đã hoàn thành tất cả các flashcard! Nhấn "Start Learning" để bắt đầu lại.** ✨')
    else:
        st.success('✨ **Bạn đã hoàn thành tất cả các flashcard! Nhấn "Start Learning" để bắt đầu lại.** ✨')

if __name__ == '__main__':
    main()
