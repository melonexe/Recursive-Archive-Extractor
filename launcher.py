#!/usr/bin/env python3
"""
Recursive Zip Extractor Launcher

This script provides an easy way to launch either the GUI or command-line version
of the recursive zip extractor tool.

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import subprocess
import argparse
from pathlib import Path


def check_tkinter():
    """Check if tkinter is available for GUI mode."""
    try:
        import tkinter
        return True
    except ImportError:
        return False


def launch_gui():
    """Launch the GUI version."""
    if not check_tkinter():
        print("❌ Error: tkinter is not available. Cannot launch GUI.")
        print("Install tkinter or use the command-line version instead.")
        return 1
    
    script_dir = Path(__file__).parent
    gui_script = script_dir / "recursive_unzipper_gui.py"
    
    if not gui_script.exists():
        print(f"❌ Error: GUI script not found at {gui_script}")
        return 1
    
    try:
        subprocess.run([sys.executable, str(gui_script)], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching GUI: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️ GUI launch cancelled by user")
        return 1


def launch_cli(args):
    """Launch the command-line version with arguments."""
    script_dir = Path(__file__).parent
    cli_script = script_dir / "recursive_unzipper.py"
    
    if not cli_script.exists():
        print(f"❌ Error: CLI script not found at {cli_script}")
        return 1
    
    # Build command arguments
    cmd_args = [sys.executable, str(cli_script)] + args
    
    try:
        subprocess.run(cmd_args, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Extraction cancelled by user")
        return 1


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description='Recursive Zip Extractor Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  --gui                 Launch the graphical user interface
  --cli                 Launch command-line version (default)

GUI Mode Examples:
  python launcher.py --gui
  python launcher.py

CLI Mode Examples:
  python launcher.py --cli archive.zip
  python launcher.py --cli archive.zip -o ./extracted --cleanup
  python launcher.py --cli archive.zip --log-level DEBUG --stats

Note: If no mode is specified and no zip file is provided, GUI mode is used.
      If a zip file is provided, CLI mode is used.
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch the graphical user interface'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch the command-line version'
    )
    
    # Parse known args to allow passing through CLI arguments
    args, unknown_args = parser.parse_known_args()
    
    # Determine mode
    if args.gui:
        print("🚀 Launching Recursive Zip Extractor GUI...")
        return launch_gui()
    elif args.cli or unknown_args:
        print("🚀 Launching Recursive Zip Extractor CLI...")
        return launch_cli(unknown_args)
    else:
        # Default to GUI if available, otherwise show help
        if check_tkinter():
            print("🚀 Launching Recursive Zip Extractor GUI...")
            print("💡 Tip: Use --cli for command-line mode")
            return launch_gui()
        else:
            print("❌ GUI not available (tkinter not found)")
            print("📋 Available options:")
            parser.print_help()
            return 1


if __name__ == '__main__':
    exit(main())
