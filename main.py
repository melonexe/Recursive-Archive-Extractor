#!/usr/bin/env python3
"""
Main entry point for the Recursive Archive Extractor

This file serves as the main entry point that can launch either the GUI or CLI version
based on command line arguments. This is designed to be the main file for PyInstaller.

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import os
from pathlib import Path
import argparse

# Add the current directory to the path so we can import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # Import our modules
    from recursive_unzipper import RecursiveUnzipper, main as cli_main
    from recursive_unzipper_gui import main as gui_main
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are in the same directory.")
    sys.exit(1)


def check_gui_available():
    """Check if GUI components are available."""
    try:
        import tkinter
        return True
    except ImportError:
        return False


def show_help():
    """Show help information."""
    print("""
Recursive Archive Extractor v1.0

This tool recursively extracts nested archive files including:
- ZIP files (.zip)
- TAR files (.tar, .tar.gz, .tgz, .tar.bz2, .tbz2, .tar.xz, .txz)
- GZIP files (.gz)

USAGE:
  archive_extractor.exe                    # Launch GUI (if available)
  archive_extractor.exe --gui              # Launch GUI
  archive_extractor.exe --cli <file>       # Launch CLI mode
  archive_extractor.exe <archive_file>     # Launch CLI mode

GUI MODE:
  archive_extractor.exe
  archive_extractor.exe --gui

CLI MODE EXAMPLES:
  archive_extractor.exe archive.zip
  archive_extractor.exe archive.tar.gz --output ./extracted
  archive_extractor.exe logfile.gz --cleanup --stats
  archive_extractor.exe nested.zip --log-level DEBUG

CLI OPTIONS:
  <archive_file>              Path to archive file to extract
  -o, --output DIR           Output directory (default: same as archive)
  --log-level LEVEL          Log level: DEBUG, INFO, WARNING, ERROR
  --cleanup                  Remove archive files after extraction
  --stats                    Show extraction statistics
  --help                     Show this help message

For more detailed help on CLI mode, use:
  archive_extractor.exe --cli --help
""")


def main():
    """Main entry point for the executable."""
    # Parse arguments manually to handle both GUI and CLI modes
    args = sys.argv[1:]
    
    # Handle help requests
    if '--help' in args or '-h' in args or 'help' in args:
        show_help()
        return 0
    
    # Handle version requests
    if '--version' in args or '-v' in args:
        print("Recursive Archive Extractor v1.0")
        return 0
    
    # Check for explicit GUI request
    if '--gui' in args:
        if not check_gui_available():
            print("❌ Error: GUI is not available (tkinter not found)")
            print("Please use CLI mode instead.")
            return 1
        print("🚀 Launching Recursive Archive Extractor GUI...")
        return gui_main()
    
    # Check for explicit CLI request
    if '--cli' in args:
        # Remove --cli from args and pass the rest to CLI
        filtered_args = [arg for arg in args if arg != '--cli']
        sys.argv = ['recursive_unzipper.py'] + filtered_args
        print("🚀 Launching Recursive Archive Extractor CLI...")
        return cli_main()
    
    # If there are arguments that look like file paths, assume CLI mode
    if args and not args[0].startswith('-'):
        # Check if the first argument looks like a file path
        potential_file = Path(args[0])
        if potential_file.exists() or '.' in args[0]:
            sys.argv = ['recursive_unzipper.py'] + args
            print("🚀 Launching Recursive Archive Extractor CLI...")
            return cli_main()
    
    # Default behavior: try GUI first, fall back to help
    if check_gui_available():
        if not args:  # No arguments provided
            print("🚀 Launching Recursive Archive Extractor GUI...")
            print("💡 Tip: Use --help for command line options")
            return gui_main()
    
    # No GUI available and no clear CLI request
    print("Recursive Archive Extractor")
    print("=" * 30)
    if not check_gui_available():
        print("⚠️  GUI mode not available (tkinter not found)")
    print("Use --help for usage information")
    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
