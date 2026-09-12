@echo off
REM ==================================================================
REM  AeroMorse - one-click safety check
REM
REM  Keep this .bat in the SAME folder as:
REM      aeromorse_validator.exe
REM      morse_map.py          (the copy you just edited)
REM      config.py             (the copy you just edited)
REM      macro_secrets.txt     (optional, for the secrets check)
REM
REM  Double-click it. If it says PASS, the files are safe to copy
REM  onto the device. If it says FAIL, fix the line it names and run
REM  it again - do NOT copy to the device until it says PASS.
REM ==================================================================
title AeroMorse - Check my files

if not exist "%~dp0aeromorse_validator.exe" (
    echo.
    echo   aeromorse_validator.exe was not found in this folder:
    echo   %~dp0
    echo.
    echo   Put this .bat next to aeromorse_validator.exe and try again.
    echo.
    pause
    exit /b 1
)

REM Pass this folder explicitly so it always checks the files sitting
REM right here, no matter where the batch is launched from. Strip the
REM trailing backslash first - a quoted path ending in "\" would escape
REM the closing quote and be misread by Windows.
set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"
"%HERE%\aeromorse_validator.exe" "%HERE%"
