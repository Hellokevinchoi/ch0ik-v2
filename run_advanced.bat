@echo off
echo 🤖 고급 개인 AI 어시스턴트를 시작합니다...
echo.
echo 1. 필요한 패키지를 설치합니다...
pip install -r requirements.txt
echo.
echo 2. 고급 애플리케이션을 실행합니다...
echo 브라우저에서 http://localhost:8501 로 접속하세요
echo.
streamlit run advanced_app.py
pause 