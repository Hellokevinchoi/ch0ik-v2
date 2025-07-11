import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# API 키 설정 (환경 변수에서 로드하거나 직접 설정)
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)


# 페이지 설정
st.set_page_config(
    page_title="개인 AI 어시스턴트",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# 사이드바 설정
with st.sidebar:
    st.title("🤖 개인 AI 설정")
    
    # AI 모델 선택
    model = st.selectbox(
        "AI 모델 선택",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    # 온도 설정 (창의성 조절)
    temperature = st.slider(
        "창의성 수준",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="높을수록 더 창의적인 응답을 생성합니다"
    )
    
    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    # 대화 내보내기
    if st.button("대화 내보내기"):
        if st.session_state.conversation_history:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.conversation_history, f, ensure_ascii=False, indent=2)
            
            st.success(f"대화가 {filename}에 저장되었습니다!")

# 메인 화면
st.title("🤖 개인 AI 어시스턴트")
st.markdown("---")

# 채팅 인터페이스
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # OpenAI API 호출
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # AI 응답을 세션에 추가
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # 대화 기록에 추가
            st.session_state.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": prompt,
                "ai_response": full_response,
                "model": model,
                "temperature": temperature
            })
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("OpenAI API 키가 올바르게 설정되었는지 확인해주세요.")

# 하단 정보
st.markdown("---")
st.markdown("""
### 사용 방법:
1. 사이드바에서 AI 모델과 창의성 수준을 설정하세요
2. 메시지를 입력하고 Enter를 누르세요
3. AI가 실시간으로 응답을 생성합니다
4. 대화 초기화 버튼으로 새로운 대화를 시작할 수 있습니다
5. 대화 내보내기 버튼으로 대화 내용을 JSON 파일로 저장할 수 있습니다

### 설정 방법:
1. `.env` 파일을 생성하고 `OPENAI_API_KEY=your_api_key_here`를 추가하세요
2. `pip install -r requirements.txt`로 필요한 패키지를 설치하세요
3. `streamlit run app.py`로 애플리케이션을 실행하세요
""") 