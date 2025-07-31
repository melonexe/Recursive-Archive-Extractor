@echo off
echo ==========================================
echo    Archive Extractor - PyInstaller Build
echo ==========================================
echo.

REM Check if PyQt6 is installed
echo Checking PyQt6...
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo ERROR: PyQt6 is not installed!
    echo Please install it with: pip install PyQt6
    echo.
    pause
    exit /b 1
)
echo ✓ PyQt6 found

REM Check if PyInstaller is installed
echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed!
    echo Please install it with: pip install pyinstaller
    echo.
    pause
    exit /b 1
)
echo ✓ PyInstaller found

REM Check for icon file
if not exist "icon.ico" (
    echo WARNING: icon.ico not found!
    echo The executable will be built without a custom icon.
    echo You can add an icon.ico file to this directory and rebuild.
    echo.
    timeout /t 3 >nul
)

REM Clean previous build
echo.
echo Cleaning previous build files...
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q "dist"
)
if exist "build" (
    echo Removing build folder...
    rmdir /s /q "build"
)

REM Build the executable
echo.
echo Building executable...
echo This may take a few minutes...
echo.
pyinstaller build.spec

REM Check if build was successful
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo ✅ BUILD SUCCESSFUL!
    echo ==========================================
    echo.
    echo Executable location: dist\Archive_Extractor.exe
    echo.
    if exist "dist\Archive_Extractor.exe" (
        echo File size: 
        for %%A in ("dist\Archive_Extractor.exe") do echo   %%~zA bytes
        echo.
        echo You can now run: dist\Archive_Extractor.exe
    )
    echo.
    echo To create an icon:
    echo 1. Create or download a 256x256 PNG image
    echo 2. Convert it to icon.ico ^(use online converter^)
    echo 3. Place icon.ico in this directory
    echo 4. Run this build script again
    echo.
) else (
    echo.
    echo ==========================================
    echo ❌ BUILD FAILED!
    echo ==========================================
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo - Missing dependencies
    echo - Antivirus blocking the build
    echo - Insufficient disk space
    echo.
)

pause
