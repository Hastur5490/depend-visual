@echo off
cd /d "%~dp0.."
echo === Test Stage 3: Real Alpine Package curl ===
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 8
pause
