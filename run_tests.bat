:: UNTESTED (I don't have Windows to test this)

@echo off
echo Running tests...

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    exit /b 1
)

REM Load environment variables from .env
for /f "tokens=*" %%a in (.env) do (
    set %%a
)

REM Set test environment variable
set TEST_ENV=true

REM Set log file path
set LOG_FILE=logs\tests.log

REM Set Python path
set PYTHONPATH=%CD%;%CD%\src

REM Run pytest and capture output
echo Running pytest... >> "%LOG_FILE%" 2>&1
pytest --cov=src --cov-report=term-missing "tests" > temp.log 2>&1
type temp.log >> "%LOG_FILE%"
type temp.log

REM Check pytest exit code
if errorlevel 1 (
    echo Tests failed! Check %LOG_FILE% for more details.
    del temp.log
    set TEST_ENV=
    exit /b 1
) else (
    echo Tests passed!
)

REM Clean up
if exist temp.log del temp.log
set TEST_ENV=