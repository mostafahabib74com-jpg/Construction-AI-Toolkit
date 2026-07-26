@echo off
setlocal EnableExtensions
title Stop Construction AI Toolkit - Scheduling MVP

set "REPO_ROOT=%~dp0"
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"
set "VENV_PYTHON=%REPO_ROOT%\.venv-scheduling-mvp\Scripts\python.exe"
set "LAUNCHER=%REPO_ROOT%\apps\scheduling-mvp\launcher.py"
set "EXIT_CODE=0"

echo ============================================================
echo  Stop Construction AI Toolkit - Scheduling MVP
echo ============================================================

cd /d "%REPO_ROOT%" || goto :REPOSITORY_ERROR
if not exist "%VENV_PYTHON%" goto :ENVIRONMENT_ERROR
if not exist "%LAUNCHER%" goto :ENTRY_ERROR

"%VENV_PYTHON%" "%LAUNCHER%" stop
set "EXIT_CODE=%ERRORLEVEL%"
goto :FINISH

:REPOSITORY_ERROR
echo [ERROR] Could not open the repository directory: %REPO_ROOT%
set "EXIT_CODE=1"
goto :FINISH

:ENVIRONMENT_ERROR
echo [ERROR] The Scheduling MVP Python environment was not found.
echo [INFO] No managed application can be stopped without its launcher environment.
set "EXIT_CODE=1"
goto :FINISH

:ENTRY_ERROR
echo [ERROR] Application launcher not found: %LAUNCHER%
set "EXIT_CODE=1"

:FINISH
echo.
if not "%CONSTRUCTION_AI_LAUNCHER_NO_PAUSE%"=="1" pause
exit /b %EXIT_CODE%
