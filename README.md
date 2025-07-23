# Recursive Zip Extractor

A Python tool that recursively extracts nested zip files, automatically finding and extracting all zip files within zip files until no more nested archives are found.

**Available in both GUI and Command-Line versions!**

## Features

- **🖥️ Graphical User Interface**: Easy-to-use GUI for non-technical users
- **⌨️ Command Line Interface**: Full-featured CLI for power users and automation
- **Recursive Extraction**: Automatically detects and extracts nested zip files
- **Robust Error Handling**: Handles corrupted files, permission errors, and invalid zip files
- **Logging Support**: Configurable logging levels for debugging and monitoring
- **Statistics Tracking**: Optional extraction statistics reporting
- **Flexible Output**: Specify custom extraction directory or use default location
- **Cleanup Options**: Choose whether to keep or remove zip files after extraction
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### 🖥️ GUI Version (Recommended for most users)

```bash
# Launch the GUI
python launcher.py

# Or directly
python recursive_unzipper_gui.py
```

### ⌨️ Command Line Version

```bash
# Basic usage
python recursive_unzipper.py archive.zip

# With cleanup and statistics
python recursive_unzipper.py archive.zip --cleanup --stats
```

## 🖥️ GUI Features

The graphical interface includes:

- **📁 File Browser**: Easy zip file and output directory selection
- **⚙️ Options Panel**: Configure log level, cleanup mode, and statistics
- **📊 Real-time Progress**: Live progress bar and status updates
- **📋 Extraction Log**: Detailed log output with timestamps
- **🎯 One-Click Operation**: Simple "Start Extraction" button
- **❌ Cancel Support**: Stop extraction if needed
- **📈 Statistics Display**: Automatic stats popup when complete

## ⌨️ Command Line Usage

### Basic Usage

```bash
python recursive_unzipper.py archive.zip
```

This will extract `archive.zip` and all nested zip files to a folder named `archive` in the same directory.

### Advanced Usage

```bash
# Extract to a specific directory
python recursive_unzipper.py archive.zip -o /path/to/extract

# Enable debug logging to see detailed extraction process
python recursive_unzipper.py archive.zip --log-level DEBUG

# Show extraction statistics
python recursive_unzipper.py archive.zip --stats

# Remove zip files after extraction (saves space)
python recursive_unzipper.py archive.zip --cleanup --stats

# Combine options
python recursive_unzipper.py archive.zip -o ./extracted --log-level INFO --cleanup --stats
```

### Command Line Options

- `zip_file`: Path to the zip file to extract (required)
- `-o, --output`: Output directory for extraction (optional, defaults to zip file's directory)
- `--log-level`: Set logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--stats`: Show extraction statistics at the end
- `--cleanup`: Remove zip files after extracting them (saves disk space)

## 🚀 Easy Launchers

### Universal Launcher
```bash
# GUI mode (default)
python launcher.py

# Command-line mode
python launcher.py --cli archive.zip --cleanup --stats
```

### Windows Shortcuts
```cmd
# GUI mode
unzip_recursive.bat
unzip_recursive.bat GUI

# CLI mode
unzip_recursive.bat archive.zip
unzip_recursive.bat archive.zip C:\extracted
```

### PowerShell
```powershell
# GUI mode
.\unzip_recursive.ps1 -GUI

# CLI mode
.\unzip_recursive.ps1 archive.zip -Stats
.\unzip_recursive.ps1 archive.zip C:\extracted -Stats
```

## How It Works

1. **Initial Extraction**: Extracts the main zip file to a target directory
2. **Recursive Search**: Scans the extracted content for additional zip files
3. **Nested Extraction**: Extracts any found zip files to their own subdirectories
4. **Iteration**: Repeats the process until no more zip files are found
5. **Completion**: Reports total extractions and any errors encountered

## Example Scenarios

### Scenario 1: Simple Nested Archive
```
main.zip
├── file1.txt
├── folder1/
│   ├── file2.txt
│   └── nested.zip
│       ├── file3.txt
│       └── file4.txt
```

Result after extraction:
```
main/
├── file1.txt
├── folder1/
│   ├── file2.txt
│   ├── nested.zip
│   └── nested/
│       ├── file3.txt
│       └── file4.txt
```

### Scenario 2: Multiple Levels of Nesting
```
archive.zip
├── level1.zip
│   ├── level2.zip
│   │   ├── level3.zip
│   │   │   └── final_file.txt
```

The tool will extract all levels automatically, creating appropriate directory structures.

## Error Handling

The tool handles various error conditions gracefully:

- **Invalid Zip Files**: Skips corrupted or invalid zip files with warning messages
- **Permission Errors**: Reports access issues but continues with other files
- **File Not Found**: Clear error messages for missing files
- **Disk Space**: Standard system errors for insufficient disk space

## Logging Levels

- **DEBUG**: Detailed information about every operation
- **INFO**: General progress information (default)
- **WARNING**: Important issues that don't stop execution
- **ERROR**: Critical errors that prevent extraction

## Performance Considerations

- The tool processes files sequentially for reliability
- Memory usage scales with the size of individual zip files, not the total archive size
- Large nested archives may take significant time to process completely
- Consider available disk space before extracting large nested archives

## Safety Features

- **Duplicate Prevention**: Tracks processed files to avoid infinite loops
- **Validation**: Verifies zip file integrity before extraction
- **Logging**: Comprehensive logging for troubleshooting and monitoring
- **Graceful Interruption**: Handles Ctrl+C interruption cleanly

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## License

This tool is provided as-is for educational and practical use.
