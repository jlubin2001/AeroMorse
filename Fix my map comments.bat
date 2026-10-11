@echo off
REM ==================================================================
REM  AeroMorse - fix my map comments
REM
REM  Keep this .bat next to morse_map_comments.py and your morse_map.py.
REM  Double-click it after changing the codes in morse_map.py: it
REM  rewrites the dots and dashes at the start of each comment so they
REM  match the binary number on the same line. Nothing else changes,
REM  and the device behaves the same - comments are only for reading.
REM
REM  It lists every comment it changed and keeps a copy of the file as
REM  it was (morse_map.py.before-comments-....bak). READ THE LIST: if a
REM  new pattern is not the one you meant, the NUMBER on that line is
REM  wrong, not the comment.
REM
REM  Needs Python.
REM ==================================================================
title AeroMorse - Fix my map comments

if not exist "%~dp0morse_map_comments.py" (
    echo.
    echo   morse_map_comments.py was not found in this folder:
    echo   %~dp0
    echo.
    echo   Put this .bat next to morse_map_comments.py and try again.
    echo.
    pause
    exit /b 1
)

set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"
python "%HERE%\morse_map_comments.py" "%HERE%"
echo.
pause
