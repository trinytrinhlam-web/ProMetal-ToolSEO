@echo off
rem Bam dup file nay de dat (hoac doi) mat khau dang nhap SEO App.
setlocal
cd /d "%~dp0"
title SEO App - Dat mat khau

set "PATH=%USERPROFILE%\.local\bin;%PATH%"

where uv >nul 2>nul
if errorlevel 1 (
    echo Chua co uv. Hay bam dup run.bat mot lan truoc, sau do chay lai file nay.
    pause
    exit /b 1
)

uv run python scripts/hash_password.py
pause
