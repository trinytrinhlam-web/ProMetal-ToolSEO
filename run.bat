@echo off
rem Bam dup file nay de mo SEO App tren Windows.
setlocal
cd /d "%~dp0"
title SEO App

set "PATH=%USERPROFILE%\.local\bin;%PATH%"

where uv >nul 2>nul
if errorlevel 1 (
    echo Chua co uv tren may. Dang cai dat uv lan dau, vui long cho...
    powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
)

where uv >nul 2>nul
if errorlevel 1 (
    echo.
    echo Khong cai duoc uv. Kiem tra ket noi mang roi thu lai,
    echo hoac xem muc "Xu ly su co" trong README.md.
    pause
    exit /b 1
)

echo Dang kiem tra va cai thu vien (lan dau co the mat vai phut)...
uv sync
if errorlevel 1 (
    echo.
    echo Cai thu vien bi loi. Chup man hinh cua so nay de nho ho tro.
    pause
    exit /b 1
)

echo.
echo Dang mo SEO App trong trinh duyet...
echo De TAT app: dong cua so nay.
echo.
uv run streamlit run app/main.py
pause
