# PowerShell script to run the recursive unzipper tool
# Usage: .\unzip_recursive.ps1 [-GUI] [<zip_file>] [output_directory]

param(
    [Parameter(Mandatory=$false)]
    [switch]$GUI,
    
    [Parameter(Mandatory=$false)]
    [string]$ZipFile = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDirectory = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$LogLevel = "INFO",
    
    [Parameter(Mandatory=$false)]
    [switch]$Stats
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LauncherScript = Join-Path $ScriptDir "launcher.py"

# Check if the launcher script exists
if (-not (Test-Path $LauncherScript)) {
    Write-Error "Launcher script not found at: $LauncherScript"
    exit 1
}

# Launch GUI mode if requested or no zip file provided
if ($GUI -or (-not $ZipFile)) {
    Write-Host "🚀 Launching Recursive Unzipper GUI..." -ForegroundColor Green
    try {
        & python $LauncherScript --gui
        exit $LASTEXITCODE
    } catch {
        Write-Error "Failed to launch GUI: $_"
        exit 1
    }
}

# CLI mode
if (-not $ZipFile) {
    Write-Error "Zip file is required for CLI mode"
    Write-Host "Usage: .\unzip_recursive.ps1 [-GUI] [<zip_file>] [output_directory]" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\unzip_recursive.ps1 -GUI" -ForegroundColor Gray
    Write-Host "  .\unzip_recursive.ps1 archive.zip" -ForegroundColor Gray
    Write-Host "  .\unzip_recursive.ps1 archive.zip C:\extracted -Stats" -ForegroundColor Gray
    exit 1
}

# Check if the zip file exists
if (-not (Test-Path $ZipFile)) {
    Write-Error "Zip file not found: $ZipFile"
    exit 1
}

# Build the command arguments for CLI mode
$Arguments = @("$LauncherScript", "--cli", "$ZipFile")

if ($OutputDirectory) {
    $Arguments += "-o"
    $Arguments += "$OutputDirectory"
}

$Arguments += "--log-level"
$Arguments += "$LogLevel"

if ($Stats) {
    $Arguments += "--stats"
}

# Run the recursive unzipper in CLI mode
Write-Host "🚀 Running recursive unzipper CLI..." -ForegroundColor Green
Write-Host "Command: python $($Arguments -join ' ')" -ForegroundColor Gray

try {
    & python @Arguments
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Extraction completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Extraction failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Error "Failed to run the recursive unzipper: $_"
    exit 1
}
