@echo off
cd /d "%~dp0.."
echo === Тест ошибки: Файл тестового репозитория не существует ===
py src/main.py -p A -r non_existent_file.txt -t -v 1.0.0
pause