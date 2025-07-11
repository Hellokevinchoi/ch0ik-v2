import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import base64
from PIL import Image
import io

# 환경 변수 로드
load_dotenv()

# API 키 설정 (환경 변수에서 로드하거나 직접 설정)
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화 (API 키가 없으면 None으로 설정)
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

# 페이지 설정
st.set_page_config(
    page_title="고급 개인 AI 어시스턴트",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "당신은 도움이 되는 AI 어시스턴트입니다."

# 파일 업로드 처리 함수
def process_uploaded_file(uploaded_file):
    """업로드된 파일을 처리하고 내용을 반환합니다."""
    try:
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            return f"업로드된 텍스트 파일 내용:\n\n{content}"
        elif uploaded_file.type.startswith("image/"):
            # 이미지를 base64로 인코딩
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"이미지가 업로드되었습니다. 이미지 분석을 요청해주세요."
        else:
            return f"지원되지 않는 파일 형식입니다: {uploaded_file.type}"
    except Exception as e:
        return f"파일 처리 중 오류가 발생했습니다: {str(e)}"

# 이미지 분석 함수
def analyze_image(image_data, prompt):
    """이미지를 분석하는 함수"""
    try:
        if client is None:
            return "OpenAI API 키가 설정되지 않아 이미지 분석을 할 수 없습니다."
        
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"이미지 분석 중 오류가 발생했습니다: {str(e)}"

# 사이드바 설정
with st.sidebar:
    st.title("🤖 고급 AI 설정")
    
    # AI 모델 선택
    model = st.selectbox(
        "AI 모델 선택",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0
    )
    
    # 온도 설정
    temperature = st.slider(
        "창의성 수준",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="높을수록 더 창의적인 응답을 생성합니다"
    )
    
    # 시스템 프롬프트 설정
    st.subheader("시스템 프롬프트 설정")
    system_prompt = st.text_area(
        "AI의 역할과 행동을 정의하세요",
        value=st.session_state.system_prompt,
        height=150
    )
    
    if st.button("시스템 프롬프트 적용"):
        st.session_state.system_prompt = system_prompt
        st.success("시스템 프롬프트가 적용되었습니다!")
    
    # 파일 업로드
    st.subheader("📁 파일 업로드")
    uploaded_file = st.file_uploader(
        "텍스트 파일 또는 이미지를 업로드하세요",
        type=["txt", "png", "jpg", "jpeg"],
        help="텍스트 파일은 내용을 분석하고, 이미지는 AI가 분석할 수 있습니다."
    )
    
    if uploaded_file is not None:
        file_content = process_uploaded_file(uploaded_file)
        st.session_state.messages.append({"role": "user", "content": file_content})
        st.success("파일이 업로드되었습니다!")
    
    # 대화 초기화
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
st.title("🤖 고급 개인 AI 어시스턴트")
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
            if client is None:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                st.info("""
                API 키를 설정하는 방법:
                1. .env 파일을 생성하고 OPENAI_API_KEY=your_api_key_here를 추가하세요
                2. 또는 환경 변수 OPENAI_API_KEY를 설정하세요
                """)
            else:
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
                    "temperature": temperature,
                    "system_prompt": st.session_state.system_prompt
                })
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("OpenAI API 키가 올바르게 설정되었는지 확인해주세요.")

# 이미지 분석 섹션
st.markdown("---")
st.subheader("🖼️ 이미지 분석")

# 이미지 업로드
image_file = st.file_uploader(
    "분석할 이미지를 업로드하세요",
    type=["png", "jpg", "jpeg"],
    key="image_analyzer"
)

if image_file is not None:
    # 이미지 표시
    image = Image.open(image_file)
    st.image(image, caption="업로드된 이미지", use_column_width=True)
    
    # 이미지 분석 프롬프트
    analysis_prompt = st.text_area(
        "이미지 분석 요청사항을 입력하세요",
        value="이 이미지에 대해 자세히 설명해주세요.",
        height=100
    )
    
    if st.button("이미지 분석 시작"):
        with st.spinner("이미지를 분석하고 있습니다..."):
            # 이미지를 base64로 인코딩
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # 이미지 분석
            analysis_result = analyze_image(img_str, analysis_prompt)
            
            st.markdown("### 분석 결과:")
            st.markdown(analysis_result)

# 하단 정보
st.markdown("---")
st.markdown("""
### 🚀 고급 기능:

1. **시스템 프롬프트 설정**: AI의 역할과 행동을 커스터마이징
2. **파일 업로드**: 텍스트 파일과 이미지 업로드 지원
3. **이미지 분석**: GPT-4 Vision을 사용한 이미지 분석
4. **대화 관리**: 대화 초기화 및 내보내기
5. **실시간 스트리밍**: AI 응답 실시간 표시

### 📋 사용 팁:

- 시스템 프롬프트로 AI의 전문 분야를 설정하세요
- 이미지 분석은 GPT-4 Vision 모델을 사용합니다
- 대화 내보내기로 중요한 대화를 보관하세요
- 파일 업로드로 문서나 이미지를 AI와 함께 분석하세요

### 설정 방법:
1. `.env` 파일을 생성하고 `OPENAI_API_KEY=your_api_key_here`를 추가하세요
2. `pip install -r requirements.txt`로 필요한 패키지를 설치하세요
3. `streamlit run advanced_app.py`로 애플리케이션을 실행하세요
""")