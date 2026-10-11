@echo off
REM ==================================================================
REM  AeroMorse - fix my map comments
REM
REM  Keep this .bat next to your morse_map.py, together with
REM  morse_map_comments.exe (or morse_map_comments.py if you have
REM  Python). Double-click it after changing the codes in morse_map.py:
REM  it rewrites the dots and dashes at the start of each comment so
REM  they match the binary number on the same line. Nothing else
REM  changes, and the device behaves the same - comments are only for
REM  reading.
REM
REM  It lists every comment it changed and keeps a copy of the file as
REM  it was (morse_map.py.before-comments-....bak). READ THE LIST: if a
REM  new pattern is not the one you meant, the NUMBER on that line is
REM  wrong, not the comment.
REM ==================================================================
title AeroMorse - Fix my map comments

set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"

if exist "%HERE%\morse_map_comments.exe" (
    "%HERE%\morse_map_comments.exe" "%HERE%"
    exit /b
)
if exist "%HERE%\morse_map_comments.py" (
    python "%HERE%\morse_map_comments.py" "%HERE%"
    echo.
    pause
    exit /b
)
echo.
echo   morse_map_comments.exe was not found in this folder:
echo   %HERE%
echo.
echo   Put this .bat next to morse_map_comments.exe and try again.
echo.
pause
exit /b 1
