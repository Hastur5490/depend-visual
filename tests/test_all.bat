@echo off
cd /d "%~dp0.."
echo 1. Успешный запуск:
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 8.8.0-r0 -f lib
echo.
echo 2. Ошибка URL:
py src/main.py -p curl -r not_a_valid_url -v 8.8.0-r0
echo.
echo 3. Ошибка пустого пакета:
py src/main.py -p "   " -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 3.20.0
echo.
echo 4. Ошибка отсутствующего файла графа:
py src/main.py -p A -r non_existent_file.txt -t -v 1.0.0
echo.
pause