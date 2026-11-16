@echo off
cd /d "%~dp0.."
echo Тест: Успешный запуск (Alpine Linux)
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 8.14.1-r2 -f lib
pause