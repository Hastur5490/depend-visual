@echo off
cd /d "%~dp0.."
echo === Test Stage 5: Mermaid Visualization (Test Graph) ===
py src/main.py -p A -r test_repos/graph_diamond.txt -t -v 1.0.0
pause
