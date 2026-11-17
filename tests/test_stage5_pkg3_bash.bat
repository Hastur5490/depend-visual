@echo off
cd /d "%~dp0.."
echo === Test Stage 5: Mermaid Visualization (Package 3: bash) ===
py src/main.py -p bash -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 5
pause
