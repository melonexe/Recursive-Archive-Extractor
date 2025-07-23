#!/usr/bin/env python3
"""
Create test .gz files for testing the recursive extractor with gzip support.
"""

import gzip
from pathlib import Path


def create_test_gz_files():
    """Create test .gz files to test gzip extraction."""
    
    # Create a simple text file and compress it
    test_content = """This is a test log file that has been compressed with gzip.
Line 1: Application started successfully
Line 2: User login attempt from 192.168.1.100
Line 3: Database connection established
Line 4: Processing 1000 records
Line 5: Operation completed successfully
Line 6: Application shutdown gracefully
"""
    
    # Create test.log.gz
    test_log_gz = Path("test.log.gz")
    with gzip.open(test_log_gz, 'wt', encoding='utf-8') as f:
        f.write(test_content)
    print(f"✅ Created {test_log_gz}")
    
    # Create another compressed file
    config_content = """# Configuration file
server.port=8080
database.url=jdbc:mysql://localhost:3306/mydb
log.level=INFO
max.connections=100
"""
    
    config_gz = Path("config.properties.gz")
    with gzip.open(config_gz, 'wt', encoding='utf-8') as f:
        f.write(config_content)
    print(f"✅ Created {config_gz}")
    
    print("\nTest .gz files created! You can now test with:")
    print(f"  python recursive_unzipper.py {test_log_gz}")
    print(f"  python recursive_unzipper.py {config_gz}")
    print(f"Or use the GUI: python launcher.py")


if __name__ == '__main__':
    create_test_gz_files()
