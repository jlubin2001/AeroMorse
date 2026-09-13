@echo off
REM ==================================================================
REM  AeroMorse - rebuild the printable PDFs from their sources.
REM
REM  Run this after editing any of:
REM      AEROMORSE_BUILD_GUIDE.md      -> AEROMORSE_BUILD_GUIDE.pdf
REM      aeromorse_cheatsheet.htm      -> AeroMorse Cheat Sheet.pdf
REM      morse_map.py                     (feeds the cheat sheet)
REM      keycode_reference.htm         -> AeroMorse - Keycode Reference.pdf
REM
REM  Rebuilds all three. To rebuild just one, add an argument:
REM      Build PDFs.bat guide        (or  cheatsheet  or  keycode )
REM  Needs Microsoft Edge and Python.
REM ==================================================================
title AeroMorse - Build PDFs

python "%~dp0build_pdfs.py" %*

echo.
pause
