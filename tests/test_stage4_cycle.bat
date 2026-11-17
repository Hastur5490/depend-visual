@echo off
cd /d "%~dp0.."
echo === Test Stage 4: Load Order (Cyclic Graph) ===
py src/main.py -p A -r test_repos/graph_cycle.txt -t -v 1.0.0 -l
pause
