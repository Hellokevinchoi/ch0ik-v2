@echo off
echo 🤖 개인 AI 어시스턴트 GUI 런처를 시작합니다...
echo.

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    pause
    exit /b 1
)

REM GUI 앱 실행
echo GUI 런처를 시작합니다...
python app_launcher.py

pause 