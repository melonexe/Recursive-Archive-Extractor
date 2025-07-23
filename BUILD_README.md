# Building the Executable

This directory contains everything needed to build a standalone executable of the Recursive Archive Extractor.

## Quick Build

### Option 1: Using Batch File (Recommended for Windows)
```cmd
build_exe.bat
```

### Option 2: Using PowerShell
```powershell
.\build_exe.ps1
```

### Option 3: Manual Build
```cmd
pip install pyinstaller
pyinstaller archive_extractor.spec
```

## What Gets Built

The build process creates:
- `dist/Archive_Extractor.exe` - The standalone executable (approximately 15-25 MB)
- No external dependencies required
- Includes both GUI and CLI functionality

## Using the Executable

### GUI Mode (Default)
```cmd
Archive_Extractor.exe
Archive_Extractor.exe --gui
```

### CLI Mode
```cmd
Archive_Extractor.exe archive.zip
Archive_Extractor.exe archive.tar.gz --output ./extracted
Archive_Extractor.exe logfile.gz --cleanup --stats
```

### Help
```cmd
Archive_Extractor.exe --help
```

## Distribution

The executable in `dist/Archive_Extractor.exe` is completely self-contained and can be:
- Copied to any Windows computer (Windows 7+)
- Run without installing Python or any dependencies
- Distributed as a single file

## Build Requirements

- Python 3.6 or higher
- PyInstaller (automatically installed by build scripts)
- All source files in the same directory

## Troubleshooting

### Build Fails
- Ensure Python is properly installed and in PATH
- Check that all source files are present
- Try running: `pip install --upgrade pyinstaller`

### Executable Won't Run
- Check Windows Defender/antivirus (may quarantine new executables)
- Ensure target computer has Windows 7 or higher
- Try running from command prompt to see error messages

### Large File Size
- The executable includes the Python interpreter and all libraries
- Size is normal for a bundled Python application (15-25 MB)
- Use UPX compression (enabled by default) to reduce size

## File Structure

```
├── main.py                    # Main entry point
├── recursive_unzipper.py      # Core extraction logic
├── recursive_unzipper_gui.py  # GUI interface
├── archive_extractor.spec     # PyInstaller configuration
├── build_exe.bat             # Windows batch build script
├── build_exe.ps1             # PowerShell build script
└── dist/                     # Output directory
    └── Archive_Extractor.exe # Final executable
```
