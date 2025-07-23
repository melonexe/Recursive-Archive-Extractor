# PowerShell build script for creating the executable using PyInstaller

Write-Host "Building Recursive Archive Extractor executable..." -ForegroundColor Green
Write-Host ""

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
} catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install PyInstaller. Please install it manually:" -ForegroundColor Red
        Write-Host "pip install pyinstaller" -ForegroundColor Gray
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Blue
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }

Write-Host ""

# Build the executable
Write-Host "Building executable... This may take a few minutes." -ForegroundColor Blue
Write-Host ""

& pyinstaller archive_extractor.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Build failed! Check the output above for errors." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the executable was created
if (Test-Path "dist\Archive_Extractor.exe") {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    
    $exeFile = Get-Item "dist\Archive_Extractor.exe"
    Write-Host "Executable created: dist\Archive_Extractor.exe"
    Write-Host "Size: $($exeFile.Length) bytes ($([math]::Round($exeFile.Length/1MB, 2)) MB)"
    Write-Host ""
    
    Write-Host "You can now distribute the executable file:" -ForegroundColor Cyan
    Write-Host "  dist\Archive_Extractor.exe" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Testing the executable..." -ForegroundColor Blue
    Write-Host ""
    & "dist\Archive_Extractor.exe" --version
    Write-Host ""
    Write-Host "Build completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Executable not found in dist folder." -ForegroundColor Red
    Write-Host "Check the build output for errors." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
