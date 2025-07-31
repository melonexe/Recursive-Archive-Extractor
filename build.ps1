# Archive Extractor - PyInstaller Build Script
# PowerShell version

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Archive Extractor - PyInstaller Build" -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyQt6 is installed
Write-Host "Checking PyQt6..." -ForegroundColor Yellow
try {
    python -c "import PyQt6" 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✓ PyQt6 found" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: PyQt6 is not installed!" -ForegroundColor Red
    Write-Host "Please install it with: pip install PyQt6" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✓ PyInstaller found" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: PyInstaller is not installed!" -ForegroundColor Red
    Write-Host "Please install it with: pip install pyinstaller" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for icon file
if (-not (Test-Path "icon.ico")) {
    Write-Host "WARNING: icon.ico not found!" -ForegroundColor Yellow
    Write-Host "The executable will be built without a custom icon." -ForegroundColor White
    Write-Host "You can add an icon.ico file to this directory and rebuild." -ForegroundColor White
    Write-Host ""
    Start-Sleep 3
}

# Clean previous build
Write-Host ""
Write-Host "Cleaning previous build files..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Write-Host "Removing dist folder..." -ForegroundColor Gray
    Remove-Item "dist" -Recurse -Force
}
if (Test-Path "build") {
    Write-Host "Removing build folder..." -ForegroundColor Gray
    Remove-Item "build" -Recurse -Force
}

# Build the executable
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

pyinstaller build.spec

# Check if build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\Archive_Extractor.exe" -ForegroundColor White
    Write-Host ""
    
    if (Test-Path "dist\Archive_Extractor.exe") {
        $fileSize = (Get-Item "dist\Archive_Extractor.exe").Length
        Write-Host "File size: $fileSize bytes" -ForegroundColor White
        Write-Host ""
        Write-Host "You can now run: dist\Archive_Extractor.exe" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "To create an icon:" -ForegroundColor Yellow
    Write-Host "1. Create or download a 256x256 PNG image" -ForegroundColor White
    Write-Host "2. Convert it to icon.ico (use online converter)" -ForegroundColor White
    Write-Host "3. Place icon.ico in this directory" -ForegroundColor White
    Write-Host "4. Run this build script again" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ BUILD FAILED!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above." -ForegroundColor White
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Missing dependencies" -ForegroundColor White
    Write-Host "- Antivirus blocking the build" -ForegroundColor White
    Write-Host "- Insufficient disk space" -ForegroundColor White
    Write-Host ""
}

Read-Host "Press Enter to exit"
