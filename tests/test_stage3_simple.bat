@echo off
cd /d "%~dp0.."
echo === Test Stage 3: Simple Graph ===
py src/main.py -p A -r test_repos/graph_simple.txt -t -v 1.0.0
pause
