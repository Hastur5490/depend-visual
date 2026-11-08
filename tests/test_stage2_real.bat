@echo off
cd /d "%~dp0.."
echo === Тест Этапа 2: Получение прямых зависимостей curl ===
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 8
pause