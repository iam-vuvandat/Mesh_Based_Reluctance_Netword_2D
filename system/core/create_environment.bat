@echo off
setlocal

REM Navigate to the project root (up two levels from system/core)
cd /d "%~dp0"
cd ..
cd ..


REM --- 1. Check and Create Venv ---
set "VENV_NAME=.venv"
set "PYTHON_EXE=%VENV_NAME%\Scripts\python.exe"

if exist "%VENV_NAME%\" (
    echo VENV: Already exists.
) else (
    echo VENV: Creating...
    python -m venv %VENV_NAME%
    
    if %errorlevel% neq 0 (
        echo ERROR: VENV creation failed. Check system Python PATH.
        goto end
    ) else (
        echo VENV: Created successfully.
    )
)


REM --- 2. Update PIP (Always run if Venv exists) ---
if exist "%PYTHON_EXE%" (
    echo PIP: Updating...
    call "%PYTHON_EXE%" -m pip install --upgrade pip
    
    if %errorlevel% neq 0 (
        echo WARNING: PIP update failed. Proceeding.
    ) else (
        echo PIP: Updated.
    )
)


:end
endlocal