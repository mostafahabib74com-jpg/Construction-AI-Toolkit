@echo off
setlocal EnableExtensions
title Construction AI Toolkit - Scheduling MVP

set "REPO_ROOT=%~dp0"
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "VENV_PYTHON=%REPO_ROOT%\.venv-scheduling-mvp\Scripts\python.exe"
set "REQUIREMENTS=%REPO_ROOT%\requirements-scheduling-mvp.txt"
set "LAUNCHER=%REPO_ROOT%\apps\scheduling-mvp\launcher.py"
set "EXIT_CODE=0"

echo ============================================================
echo  Construction AI Toolkit - Scheduling MVP
echo ============================================================
echo Repository: %REPO_ROOT%
echo.

cd /d "%REPO_ROOT%" || goto :REPOSITORY_ERROR

if not exist "%LAUNCHER%" goto :ENTRY_ERROR
if not exist "%REQUIREMENTS%" goto :REQUIREMENTS_ERROR
if exist "%VENV_PYTHON%" goto :CHECK_DEPENDENCIES

echo [SETUP] Python environment was not found. Creating it now...
where py >nul 2>&1
if errorlevel 1 goto :TRY_PYTHON
py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if errorlevel 1 goto :TRY_PYTHON
py -3.12 -m venv "%REPO_ROOT%\.venv-scheduling-mvp"
if errorlevel 1 goto :VENV_ERROR
goto :CHECK_DEPENDENCIES

:TRY_PYTHON
where python >nul 2>&1
if errorlevel 1 goto :PYTHON_ERROR
python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if errorlevel 1 goto :PYTHON_VERSION_ERROR
python -m venv "%REPO_ROOT%\.venv-scheduling-mvp"
if errorlevel 1 goto :VENV_ERROR

:CHECK_DEPENDENCIES
echo [CHECK] Verifying the Milestone 1 Python environment...
"%VENV_PYTHON%" -c "import streamlit, pandas, openpyxl, jsonschema, yaml, construction_ai_orchestrator, construction_ai_scheduling" >nul 2>&1
if errorlevel 1 goto :INSTALL_DEPENDENCIES
"%VENV_PYTHON%" -m pip check >nul 2>&1
if errorlevel 1 goto :INSTALL_DEPENDENCIES
echo [OK] Milestone 1 dependencies are installed and consistent.
goto :LAUNCH

:INSTALL_DEPENDENCIES
echo [SETUP] Installing missing Milestone 1 dependencies...
"%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 goto :DEPENDENCY_ERROR
"%VENV_PYTHON%" -c "import streamlit, pandas, openpyxl, jsonschema, yaml, construction_ai_orchestrator, construction_ai_scheduling" >nul 2>&1
if errorlevel 1 goto :DEPENDENCY_ERROR
echo [OK] Milestone 1 dependencies are ready.

:LAUNCH
echo [START] Starting Streamlit on http://127.0.0.1:8501
echo [INFO] Keep this window open while using the application.
echo [INFO] Runtime logs are written under apps\scheduling-mvp\logs.
echo.
"%VENV_PYTHON%" "%LAUNCHER%" run
set "EXIT_CODE=%ERRORLEVEL%"
if "%EXIT_CODE%"=="0" (
    echo [STOPPED] The Scheduling MVP is no longer running.
) else (
    echo [ERROR] The Scheduling MVP stopped with exit code %EXIT_CODE%.
    echo [ERROR] Review the newest file in apps\scheduling-mvp\logs.
)
goto :FINISH

:REPOSITORY_ERROR
echo [ERROR] Could not open the repository directory: %REPO_ROOT%
set "EXIT_CODE=1"
goto :FINISH

:ENTRY_ERROR
echo [ERROR] Application launcher not found: %LAUNCHER%
set "EXIT_CODE=1"
goto :FINISH

:REQUIREMENTS_ERROR
echo [ERROR] Requirements file not found: %REQUIREMENTS%
set "EXIT_CODE=1"
goto :FINISH

:PYTHON_ERROR
echo [ERROR] Python 3.12 was not found.
echo [ERROR] Install Python 3.12 from python.org and run this launcher again.
set "EXIT_CODE=1"
goto :FINISH

:PYTHON_VERSION_ERROR
echo [ERROR] The available python command is not Python 3.12.
echo [ERROR] Install Python 3.12 or make the py -3.12 launcher available.
set "EXIT_CODE=1"
goto :FINISH

:VENV_ERROR
echo [ERROR] The local Python environment could not be created.
set "EXIT_CODE=1"
goto :FINISH

:DEPENDENCY_ERROR
echo [ERROR] Milestone 1 dependencies could not be installed or imported.
echo [ERROR] Check your internet connection and the messages above.
set "EXIT_CODE=1"

:FINISH
echo.
if not "%CONSTRUCTION_AI_LAUNCHER_NO_PAUSE%"=="1" pause
exit /b %EXIT_CODE%
