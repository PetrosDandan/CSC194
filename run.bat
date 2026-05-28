@echo off
title Iligan City Flood Evacuation & Situation Awareness Simulator
cd %~dp0

echo ======================================================================
echo     ILIGAN CITY FLOOD EVACUATION ^& SITUATION AWARENESS SIMULATOR
echo ======================================================================
echo [*] Checking Python environment dependencies...

where python3 >nul 2>&1
if %errorlevel% neq 0 (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [-] Error: Python was not found on your system PATH!
        echo [-] Please install Python 3.x and ensure it is added to variables.
        pause
        exit /b 1
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=python3
)

echo [*] Launching click-to-run system...
%PY_CMD% run.py
pause
