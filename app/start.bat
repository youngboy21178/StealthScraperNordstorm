@echo off
echo ===================================
echo 🧪 RUNNING TESTS BEFORE START...
echo ===================================

call env\Scripts\activate.bat
pytest

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ CRITICAL: Tests failed! The scraper will NOT start.
    exit /B %ERRORLEVEL%
)

echo.
echo ✅ Tests passed! Starting the scraper...
echo ===================================
python main.py