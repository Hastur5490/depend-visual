@echo off
cd /d "%~dp0.."
echo === Тест ошибки: Пустое имя пакета ===
py src/main.py -p "   " -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 3.20.0
pause