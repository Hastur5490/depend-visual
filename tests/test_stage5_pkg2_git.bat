@echo off
cd /d "%~dp0.."
echo === Test Stage 5: Mermaid Visualization (Package 2: git) ===
py src/main.py -p git -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 2
pause
