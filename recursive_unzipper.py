#!/usr/bin/env python3
"""
Recursive Zip Extractor Tool

This tool recursively extracts nested zip files, finding and extracting
all zip files within zip files until no more nested archives are found.

Author: GitHub Copilot
Date: July 23, 2025
"""

import os
import zipfile
import tarfile
import gzip
import shutil
import argparse
import logging
from pathlib import Path
from typing import List, Set


class RecursiveUnzipper:
    """A class to handle recursive extraction of nested zip and tar archives."""
    
    # Supported archive extensions
    ARCHIVE_EXTENSIONS = {
        '.zip': 'zip',
        '.tar': 'tar',
        '.tar.gz': 'tar',
        '.tgz': 'tar', 
        '.tar.bz2': 'tar',
        '.tbz2': 'tar',
        '.tar.xz': 'tar',
        '.txz': 'tar',
        '.gz': 'gzip'
    }
    
    def __init__(self, log_level: str = 'INFO', cleanup_zips: bool = False):
        """Initialize the RecursiveUnzipper with logging configuration."""
        self.setup_logging(log_level)
        self.processed_files: Set[str] = set()
        self.extraction_count = 0
        self.cleanup_zips = cleanup_zips
        
    def setup_logging(self, log_level: str) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def is_archive_file(self, file_path: Path) -> bool:
        """Check if a file is a valid archive file (zip, tar, or gzip)."""
        # Get the archive type based on file extension
        archive_type = self.get_archive_type(file_path)
        if not archive_type:
            return False
            
        try:
            if archive_type == 'zip':
                with zipfile.ZipFile(file_path, 'r') as zf:
                    # Try to read the zip file info to validate it
                    zf.testzip()
                    return True
            elif archive_type == 'tar':
                with tarfile.open(file_path, 'r') as tf:
                    # Try to read the tar file to validate it
                    tf.getnames()
                    return True
            elif archive_type == 'gzip':
                with gzip.open(file_path, 'rb') as gz:
                    # Try to read a small portion to validate it's a valid gzip file
                    gz.read(1)
                    return True
        except Exception as e:
            self.logger.debug(f"File {file_path} is not a valid archive file: {e}")
            return False
            
        return False
        
    def get_archive_type(self, file_path: Path) -> str:
        """Determine the archive type based on file extension."""
        file_str = str(file_path).lower()
        
        # Check for compound extensions first (like .tar.gz)
        for ext, archive_type in self.ARCHIVE_EXTENSIONS.items():
            if file_str.endswith(ext):
                return archive_type
                
        return None
            
    def extract_archive_file(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract a single archive file to the specified directory."""
        try:
            self.logger.info(f"Extracting: {archive_path} to {extract_to}")
            
            # Create extraction directory if it doesn't exist
            extract_to.mkdir(parents=True, exist_ok=True)
            
            archive_type = self.get_archive_type(archive_path)
            
            if archive_type == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(extract_to)
            elif archive_type == 'tar':
                with tarfile.open(archive_path, 'r') as tf:
                    tf.extractall(extract_to)
            elif archive_type == 'gzip':
                # For standalone .gz files, extract to a file with the same name minus .gz
                output_file = extract_to / archive_path.stem
                with gzip.open(archive_path, 'rb') as gz_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(gz_in, f_out)
                self.logger.info(f"Extracted gzip file to: {output_file}")
            else:
                self.logger.error(f"Unsupported archive type for {archive_path}")
                return False
                
            self.extraction_count += 1
            self.logger.info(f"Successfully extracted {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract {archive_path}: {e}")
            return False
            
    def find_archive_files(self, directory: Path) -> List[Path]:
        """Find all archive files in a directory recursively."""
        archive_files = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    # Check if this file has a supported archive extension
                    if self.get_archive_type(item):
                        # Avoid processing the same file multiple times
                        abs_path = str(item.absolute())
                        if abs_path not in self.processed_files:
                            if self.is_archive_file(item):
                                archive_files.append(item)
                                self.processed_files.add(abs_path)
                        
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing directory {directory}: {e}")
            
        return archive_files
        
    def recursive_unzip(self, archive_path: Path, base_extract_dir: Path = None) -> bool:
        """
        Recursively extract an archive file and all nested archive files found within.
        
        Args:
            archive_path: Path to the initial archive file
            base_extract_dir: Base directory to extract to (defaults to archive file's directory)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not archive_path.exists():
            self.logger.error(f"Archive file not found: {archive_path}")
            return False
            
        if not self.is_archive_file(archive_path):
            self.logger.error(f"Invalid archive file: {archive_path}")
            return False
            
        # Set default extraction directory
        if base_extract_dir is None:
            base_extract_dir = archive_path.parent / archive_path.stem
            
        self.logger.info(f"Starting recursive extraction of {archive_path}")
        self.logger.info(f"Base extraction directory: {base_extract_dir}")
        
        # Track the original archive file as processed
        self.processed_files.add(str(archive_path.absolute()))
        
        # Extract the initial archive file
        if not self.extract_archive_file(archive_path, base_extract_dir):
            return False
            
        # Keep processing until no more archive files are found
        iteration = 1
        while True:
            self.logger.info(f"Iteration {iteration}: Searching for nested archive files...")
            
            # Find all archive files in the extraction directory
            nested_archives = self.find_archive_files(base_extract_dir)
            
            if not nested_archives:
                self.logger.info("No more nested archive files found. Extraction complete!")
                break
                
            self.logger.info(f"Found {len(nested_archives)} nested archive file(s) to extract:")
            for archive in nested_archives:
                self.logger.info(f"  - {archive.name} ({self.get_archive_type(archive)} format)")
            
            # Extract each nested archive file
            for nested_archive in nested_archives:
                # Create extraction directory for this nested archive
                nested_extract_dir = nested_archive.parent / nested_archive.stem
                self.extract_archive_file(nested_archive, nested_extract_dir)
                
                # Remove the extracted archive file if cleanup is enabled
                if self.cleanup_zips:
                    try:
                        nested_archive.unlink()
                        self.logger.debug(f"Removed extracted archive file: {nested_archive}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove {nested_archive}: {e}")
                    
            iteration += 1
            
        self.logger.info(f"Recursive extraction completed! Total extractions: {self.extraction_count}")
        return True
        
    def get_stats(self) -> dict:
        """Get extraction statistics."""
        return {
            'total_extractions': self.extraction_count,
            'processed_files': len(self.processed_files)
        }


def main():
    """Main function to handle command line arguments and run the tool."""
    parser = argparse.ArgumentParser(
        description='Recursively extract nested archive files (zip, tar.gz, tgz, tar.bz2, gz, etc.)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recursive_unzipper.py archive.zip
  python recursive_unzipper.py archive.tar.gz -o /path/to/extract
  python recursive_unzipper.py nested.tgz --log-level DEBUG
  python recursive_unzipper.py logfile.gz --cleanup --stats
        """
    )
    
    parser.add_argument(
        'archive_file',
        type=str,
        help='Path to the archive file to extract recursively (supports .zip, .tar.gz, .tgz, .tar.bz2, .gz, etc.)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory for extraction (default: same directory as zip file)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show extraction statistics at the end'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove archive files after extracting them (saves disk space)'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    archive_path = Path(args.archive_file)
    output_dir = Path(args.output) if args.output else None
    
    # Create and run the unzipper
    unzipper = RecursiveUnzipper(log_level=args.log_level, cleanup_zips=args.cleanup)
    
    try:
        success = unzipper.recursive_unzip(archive_path, output_dir)
        
        if args.stats:
            stats = unzipper.get_stats()
            print(f"\n--- Extraction Statistics ---")
            print(f"Total extractions: {stats['total_extractions']}")
            print(f"Processed files: {stats['processed_files']}")
            
        if success:
            print(f"\n✅ Successfully completed recursive extraction of {archive_path}")
            return 0
        else:
            print(f"\n❌ Failed to extract {archive_path}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Extraction interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
