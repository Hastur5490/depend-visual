@echo off
cd /d "%~dp0.."
echo === Test Stage 3: Cyclic Dependencies ===
py src/main.py -p A -r test_repos/graph_cycle.txt -t -v 1.0.0
pause
