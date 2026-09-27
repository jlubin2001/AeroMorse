@echo off
REM ==================================================================
REM  AeroMorse - one-click dated backup
REM
REM  Keep this .bat in your AeroMorse work folder. Double-click it with
REM  your AeroMorse plugged in. It copies EVERYTHING on each AeroMorse
REM  (CIRCUITPY) drive it finds into:
REM
REM      <this folder>\Backups\<name>-<YYYY-MM-DD_HHMM>\
REM
REM  <name> comes from a label file on the device, e.g. AeroMorse-Green.txt
REM  (an empty text file you create). Without one it is just "AeroMorse".
REM  Nothing on the device is changed - it only reads.
REM ==================================================================
setlocal EnableDelayedExpansion
title AeroMorse - Back up my AeroMorse
set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set "STAMP=%%i"

set FOUND=0
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\boot_out.txt" if exist "%%d:\code.py" (
        set "NAME=AeroMorse"
        for %%n in ("%%d:\AeroMorse-*.txt") do set "NAME=%%~nn"
        set "DEST=%HERE%\Backups\!NAME!-%STAMP%"
        echo.
        echo   Backing up %%d:\  ^(!NAME!^)  to
        echo   !DEST!
        robocopy "%%d:\." "!DEST!" /E /XD "System Volume Information" /NFL /NDL /NJH /NJS /NP >nul
        if !ERRORLEVEL! GEQ 8 (
            echo   FAILED - check the drive and try again.
        ) else (
            set /a FOUND+=1
            echo   Done.
        )
    )
)
echo.
if %FOUND%==0 (
    echo   No AeroMorse drive found. Plug the device in ^(it shows up as
    echo   CIRCUITPY^) and try again.
) else (
    echo   %FOUND% device^(s^) backed up. Backups are in:
    echo   %HERE%\Backups
)
echo.
pause
