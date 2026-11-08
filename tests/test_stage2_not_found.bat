@echo off
cd /d "%~dp0.."
echo === Тест Этапа 2: Ошибка (несуществующая версия) ===
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 99.99.99
pause