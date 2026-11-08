@echo off
py src/main.py -p alpine-base -r https://dl-cdn.alpinelinux.org/alpine/v3.20/main -v 3.20.0 -f musl
pause