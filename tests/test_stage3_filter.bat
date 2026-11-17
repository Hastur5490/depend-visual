@echo off
cd /d "%~dp0.."
echo === Test Stage 3: Filter Substring TEST ===
py src/main.py -p A -r test_repos/graph_filter.txt -t -v 1.0.0 -f TEST
pause
