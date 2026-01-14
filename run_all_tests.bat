@echo off
REM Master Test Runner for Windows
REM Runs complete security testing suite and generates comprehensive reports

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo UI SECURITY VULNERABILITY TESTING SUITE - WINDOWS
echo ================================================================================
echo.

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo [!] Python is not installed or not in PATH
    exit /b 1
)

echo [*] Python found:
python --version

REM Set up working directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Create results directory
if not exist "results" mkdir results

echo [*] Installing dependencies...
pip install -q flask requests markupsafe click itsdangerous jinja2 werkzeug flask-talisman python-dotenv

echo.
echo ================================================================================
echo PHASE 1: TESTING VULNERABLE (PRE-MITIGATION) VERSION
echo ================================================================================
echo.

echo [*] Starting vulnerable Flask app on port 5000...
cd /d "%SCRIPT_DIR%pre-mitigation\app"
start /B python app.py > "%SCRIPT_DIR%results\pre_mitigation_app.log" 2>&1

REM Wait for app to start
timeout /t 3 /nobreak > nul

echo [+] App started (PID tracking unavailable on Windows)
echo [*] Running exploit tests...

cd /d "%SCRIPT_DIR%pre-mitigation\tests"
python exploit_tests.py

if exist "%SCRIPT_DIR%pre-mitigation\exploit_results.json" (
    echo [+] Exploit tests completed
    copy "%SCRIPT_DIR%pre-mitigation\exploit_results.json" "%SCRIPT_DIR%results\exploit_results.json" > nul
) else (
    echo [!] Exploit tests failed - no results generated
)

REM Kill vulnerable app
echo [*] Stopping vulnerable application...
taskkill /F /IM python.exe > nul 2>&1
timeout /t 2 /nobreak > nul

echo.
echo ================================================================================
echo PHASE 2: TESTING SECURE (POST-MITIGATION) VERSION
echo ================================================================================
echo.

REM Setup environment for secure version
if not exist "%SCRIPT_DIR%post-mitigation\app\.env" (
    echo [*] Creating .env file...
    if exist "%SCRIPT_DIR%post-mitigation\.env.example" (
        copy "%SCRIPT_DIR%post-mitigation\.env.example" "%SCRIPT_DIR%post-mitigation\app\.env" > nul
    )
)

echo [*] Starting secure Flask app on port 5001...
cd /d "%SCRIPT_DIR%post-mitigation\app"
set FLASK_DEBUG=False
set ENVIRONMENT=production
start /B python app.py > "%SCRIPT_DIR%results\post_mitigation_app.log" 2>&1

REM Wait for app to start
timeout /t 3 /nobreak > nul

echo [+] App started
echo [*] Running validation tests...

cd /d "%SCRIPT_DIR%post-mitigation\tests"
python validation_tests.py

if exist "%SCRIPT_DIR%post-mitigation\validation_results.json" (
    echo [+] Validation tests completed
    copy "%SCRIPT_DIR%post-mitigation\validation_results.json" "%SCRIPT_DIR%results\validation_results.json" > nul
) else (
    echo [!] Validation tests failed - no results generated
)

REM Kill secure app
echo [*] Stopping secure application...
taskkill /F /IM python.exe > nul 2>&1

echo.
echo ================================================================================
echo GENERATING REPORTS
echo ================================================================================
echo.

cd /d "%SCRIPT_DIR%"
python security_report_generator.py
python report_template_generator.py

echo.
echo ================================================================================
echo TEST SUMMARY
echo ================================================================================
echo.

if exist "%SCRIPT_DIR%results\exploit_results.json" (
    echo [+] Exploit test results available in: results\exploit_results.json
)

if exist "%SCRIPT_DIR%results\validation_results.json" (
    echo [+] Validation test results available in: results\validation_results.json
)

echo [+] Security reports generated:
if exist "pre_mitigation_report.json" echo     - pre_mitigation_report.json
if exist "post_mitigation_report.json" echo     - post_mitigation_report.json
if exist "report_template.json" echo     - report_template.json
if exist "REPORT_TEMPLATE.md" echo     - REPORT_TEMPLATE.md

echo.
echo [+] All test results in: %SCRIPT_DIR%results\
echo [+] Test suite completed successfully!
echo.

pause
