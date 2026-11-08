@echo off
cd /d "%~dp0.."
echo === Тест: Режим тестового репозитория ===
py src/main.py -p A -r README.md -t -v 1.0.0
pause