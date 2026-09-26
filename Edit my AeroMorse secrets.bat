@echo off
REM ==================================================================
REM  AeroMorse - edit your passwords (PIN-locked macro_secrets.enc)
REM
REM  Keep this .bat in the SAME folder as:
REM      AeroMorse Secrets.exe
REM      morse_map.py          (so it can check your _secret() keys)
REM      macro_secrets.txt / macro_secrets.enc
REM
REM  Double-click it: AeroMorse Secrets opens the secrets in THIS folder.
REM ==================================================================
set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"
if not exist "%HERE%\AeroMorse Secrets.exe" (
    echo.
    echo   AeroMorse Secrets.exe was not found in this folder:
    echo   %HERE%
    echo.
    pause
    exit /b 1
)
start "" "%HERE%\AeroMorse Secrets.exe" "%HERE%"
