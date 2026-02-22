@echo off
echo ===================================
echo [TESTS] RUNNING TESTS BEFORE START...
echo ===================================

env\Scripts\python.exe -m pytest

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] CRITICAL: Tests failed! The scraper will NOT start.
    exit /B %ERRORLEVEL%
)

echo.
echo [SUCCESS] Tests passed! Starting the scraper...
echo ===================================

set PYTHONPATH=.

env\Scripts\python.exe app\main.py