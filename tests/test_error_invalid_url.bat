@echo off
cd /d "%~dp0.."
echo === Тест ошибки: Невалидный URL репозитория ===
py src/main.py -p curl -r not_a_valid_url -v 8.8.0-r0
pause