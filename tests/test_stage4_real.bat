@echo off
cd /d "%~dp0.."
echo === Test Stage 4: Load Order (Real Package curl) ===
py src/main.py -p curl -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 8 -l
pause
