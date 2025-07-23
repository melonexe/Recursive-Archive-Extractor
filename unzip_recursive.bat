@echo off
REM Batch script to run the recursive unzipper tool
REM Usage: unzip_recursive.bat [GUI] [zip_file] [output_directory]

if "%1"=="GUI" (
    echo Starting Recursive Unzipper GUI...
    python "%~dp0launcher.py" --gui
    goto :end
)

if "%1"=="" (
    echo Starting Recursive Unzipper GUI...
    python "%~dp0launcher.py" --gui
    goto :end
)

if "%1"=="/?" (
    echo Usage: unzip_recursive.bat [GUI] [zip_file] [output_directory]
    echo.
    echo Examples:
    echo   unzip_recursive.bat GUI
    echo   unzip_recursive.bat archive.zip
    echo   unzip_recursive.bat archive.zip C:\extracted
    echo.
    pause
    exit /b 0
)

set ZIP_FILE=%1
set OUTPUT_DIR=%2

if "%OUTPUT_DIR%"=="" (
    python "%~dp0launcher.py" --cli "%ZIP_FILE%" --stats
) else (
    python "%~dp0launcher.py" --cli "%ZIP_FILE%" -o "%OUTPUT_DIR%" --stats
)

:end
pause
