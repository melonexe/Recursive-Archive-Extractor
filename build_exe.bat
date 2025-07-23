@echo off
REM Build script for creating the executable using PyInstaller

echo Building Recursive Archive Extractor executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller. Please install it manually:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo Cleaning previous builds...
echo.

REM Build the executable
echo Building executable... This may take a few minutes.
echo.

pyinstaller archive_extractor.spec

if errorlevel 1 (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    pause
    exit /b 1
)

REM Check if the executable was created
if exist "dist\Archive_Extractor.exe" (
    echo.
    echo ✅ Build successful!
    echo.
    echo Executable created: dist\Archive_Extractor.exe
    echo Size: 
    for %%I in ("dist\Archive_Extractor.exe") do echo %%~zI bytes
    echo.
    echo You can now distribute the executable file:
    echo   dist\Archive_Extractor.exe
    echo.
    echo Testing the executable...
    echo.
    "dist\Archive_Extractor.exe" --version
    echo.
    echo Build completed successfully!
) else (
    echo.
    echo ❌ Executable not found in dist folder.
    echo Check the build output for errors.
)

echo.
pause
