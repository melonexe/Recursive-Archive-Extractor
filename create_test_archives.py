#!/usr/bin/env python3
"""
Test script for the Recursive Archive Extractor

This script creates sample nested archive files (zip and tar.gz) for testing the recursive extractor.
"""

import os
import zipfile
import tarfile
import tempfile
from pathlib import Path


def create_test_files():
    """Create sample files for testing."""
    files = {}
    
    # Create some sample text content
    files['file1.txt'] = "This is file 1 content"
    files['file2.txt'] = "This is file 2 content"
    files['file3.txt'] = "This is file 3 content"
    files['file4.txt'] = "This is file 4 content"
    files['deep_file.txt'] = "This file is deeply nested!"
    
    return files


def create_nested_zip_structure(base_dir: Path):
    """Create a complex nested zip structure for testing."""
    
    files = create_test_files()
    
    # Create temporary directory for file creation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create the deepest level zip (level3.zip)
        level3_dir = temp_path / "level3"
        level3_dir.mkdir()
        
        # Write deep file
        (level3_dir / "deep_file.txt").write_text(files['deep_file.txt'])
        
        # Create level3.zip
        level3_zip = temp_path / "level3.zip"
        with zipfile.ZipFile(level3_zip, 'w') as zf:
            zf.write(level3_dir / "deep_file.txt", "deep_file.txt")
        
        # Create level2 directory and zip
        level2_dir = temp_path / "level2"
        level2_dir.mkdir()
        
        # Copy level3.zip to level2 directory
        (level2_dir / "level3.zip").write_bytes(level3_zip.read_bytes())
        (level2_dir / "file3.txt").write_text(files['file3.txt'])
        
        # Create level2.zip
        level2_zip = temp_path / "level2.zip"
        with zipfile.ZipFile(level2_zip, 'w') as zf:
            zf.write(level2_dir / "level3.zip", "level3.zip")
            zf.write(level2_dir / "file3.txt", "file3.txt")
        
        # Create level1 directory and zip
        level1_dir = temp_path / "level1"
        level1_dir.mkdir()
        
        # Copy level2.zip to level1 directory
        (level1_dir / "level2.zip").write_bytes(level2_zip.read_bytes())
        (level1_dir / "file2.txt").write_text(files['file2.txt'])
        
        # Create level1.zip
        level1_zip = temp_path / "level1.zip"
        with zipfile.ZipFile(level1_zip, 'w') as zf:
            zf.write(level1_dir / "level2.zip", "level2.zip")
            zf.write(level1_dir / "file2.txt", "file2.txt")
        
        # Create the main test zip
        main_test_dir = temp_path / "main_test"
        main_test_dir.mkdir()
        
        # Add some files to main directory
        (main_test_dir / "file1.txt").write_text(files['file1.txt'])
        (main_test_dir / "file4.txt").write_text(files['file4.txt'])
        
        # Create a subdirectory with another zip
        sub_dir = main_test_dir / "subdirectory"
        sub_dir.mkdir()
        (sub_dir / "level1.zip").write_bytes(level1_zip.read_bytes())
        
        # Create the final test zip
        test_zip_path = base_dir / "test_nested_archive.zip"
        with zipfile.ZipFile(test_zip_path, 'w') as zf:
            # Add main files
            zf.write(main_test_dir / "file1.txt", "file1.txt")
            zf.write(main_test_dir / "file4.txt", "file4.txt")
            
            # Add subdirectory and its contents
            zf.write(sub_dir / "level1.zip", "subdirectory/level1.zip")
    
    return test_zip_path


def create_simple_nested_zip(base_dir: Path):
    """Create a simple nested zip for basic testing."""
    
    files = create_test_files()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create inner zip
        inner_dir = temp_path / "inner"
        inner_dir.mkdir()
        (inner_dir / "inner_file.txt").write_text("Content from inner zip file")
        
        inner_zip = temp_path / "inner.zip"
        with zipfile.ZipFile(inner_zip, 'w') as zf:
            zf.write(inner_dir / "inner_file.txt", "inner_file.txt")
        
        # Create outer zip structure
        outer_dir = temp_path / "outer"
        outer_dir.mkdir()
        (outer_dir / "outer_file.txt").write_text("Content from outer zip file")
        (outer_dir / "inner.zip").write_bytes(inner_zip.read_bytes())
        
        # Create final simple zip
        simple_zip_path = base_dir / "simple_nested_archive.zip"
        with zipfile.ZipFile(simple_zip_path, 'w') as zf:
            zf.write(outer_dir / "outer_file.txt", "outer_file.txt")
            zf.write(outer_dir / "inner.zip", "inner.zip")
    
def create_mixed_archive_structure(base_dir: Path):
    """Create a mixed archive structure with both zip and tar.gz files for testing."""
    
    files = create_test_files()
    
    # Create temporary directory for file creation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create the deepest level as tar.gz (level3.tar.gz)
        level3_dir = temp_path / "level3"
        level3_dir.mkdir()
        
        # Write deep file
        (level3_dir / "deep_file.txt").write_text(files['deep_file.txt'])
        
        # Create level3.tar.gz
        level3_tgz = temp_path / "level3.tar.gz"
        with tarfile.open(level3_tgz, 'w:gz') as tf:
            tf.add(level3_dir / "deep_file.txt", "deep_file.txt")
        
        # Create level2 directory with .tgz file
        level2_dir = temp_path / "level2"
        level2_dir.mkdir()
        
        # Copy level3.tar.gz as level3.tgz to level2 directory
        level3_tgz_copy = level2_dir / "level3.tgz"
        level3_tgz_copy.write_bytes(level3_tgz.read_bytes())
        (level2_dir / "file3.txt").write_text(files['file3.txt'])
        
        # Create level2.zip (mixing formats)
        level2_zip = temp_path / "level2.zip"
        with zipfile.ZipFile(level2_zip, 'w') as zf:
            zf.write(level2_dir / "level3.tgz", "level3.tgz")
            zf.write(level2_dir / "file3.txt", "file3.txt")
        
        # Create level1 directory with tar.bz2
        level1_dir = temp_path / "level1"
        level1_dir.mkdir()
        
        # Copy level2.zip to level1 directory
        (level1_dir / "level2.zip").write_bytes(level2_zip.read_bytes())
        (level1_dir / "file2.txt").write_text(files['file2.txt'])
        
        # Create level1.tar.bz2
        level1_tbz2 = temp_path / "level1.tar.bz2"
        with tarfile.open(level1_tbz2, 'w:bz2') as tf:
            tf.add(level1_dir / "level2.zip", "level2.zip")
            tf.add(level1_dir / "file2.txt", "file2.txt")
        
        # Create the main test zip with mixed content
        main_test_dir = temp_path / "main_test"
        main_test_dir.mkdir()
        
        # Add some files to main directory
        (main_test_dir / "file1.txt").write_text(files['file1.txt'])
        (main_test_dir / "file4.txt").write_text(files['file4.txt'])
        
        # Create a subdirectory with mixed archives
        sub_dir = main_test_dir / "subdirectory"
        sub_dir.mkdir()
        (sub_dir / "level1.tar.bz2").write_bytes(level1_tbz2.read_bytes())
        
        # Also add a simple .tgz file
        simple_tgz_dir = temp_path / "simple_tgz_content"
        simple_tgz_dir.mkdir()
        (simple_tgz_dir / "simple_tgz_file.txt").write_text("Content from simple TGZ file")
        
        simple_tgz = sub_dir / "simple.tgz"
        with tarfile.open(simple_tgz, 'w:gz') as tf:
            tf.add(simple_tgz_dir / "simple_tgz_file.txt", "simple_tgz_file.txt")
        
        # Create the final mixed test archive as zip
        mixed_zip_path = base_dir / "mixed_nested_archive.zip"
        with zipfile.ZipFile(mixed_zip_path, 'w') as zf:
            # Add main files
            zf.write(main_test_dir / "file1.txt", "file1.txt")
            zf.write(main_test_dir / "file4.txt", "file4.txt")
            
            # Add subdirectory and its contents
            zf.write(sub_dir / "level1.tar.bz2", "subdirectory/level1.tar.bz2")
            zf.write(simple_tgz, "subdirectory/simple.tgz")
    
    return mixed_zip_path


def main():
    """Create test archive files for the recursive extractor."""
    
    current_dir = Path.cwd()
    
    print("Creating test archive files...")
    
    # Create simple nested zip
    simple_zip = create_simple_nested_zip(current_dir)
    print(f"✅ Created simple test archive: {simple_zip}")
    
    # Create complex nested zip
    complex_zip = create_nested_zip_structure(current_dir)
    print(f"✅ Created complex test archive: {complex_zip}")
    
    # Create mixed format archive
    mixed_archive = create_mixed_archive_structure(current_dir)
    print(f"✅ Created mixed format test archive: {mixed_archive}")
    
    print("\nTest files created! You can now test the recursive extractor with:")
    print(f"  python recursive_unzipper.py {simple_zip.name}")
    print(f"  python recursive_unzipper.py {complex_zip.name}")
    print(f"  python recursive_unzipper.py {mixed_archive.name}")
    print(f"  python recursive_unzipper.py {mixed_archive.name} --stats --log-level DEBUG")
    print(f"\nOr use the GUI:")
    print(f"  python launcher.py")


if __name__ == '__main__':
    main()
