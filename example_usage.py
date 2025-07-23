"""
Example usage of the RecursiveUnzipper class as a module

This demonstrates how to use the recursive unzipper programmatically
in your own Python scripts.
"""

from pathlib import Path
from recursive_unzipper import RecursiveUnzipper


def example_basic_usage():
    """Example of basic programmatic usage."""
    
    # Create an instance of the unzipper
    unzipper = RecursiveUnzipper(log_level='INFO')
    
    # Specify the zip file to extract
    zip_file = Path("test_nested_archive.zip")
    
    # Extract to default location (same directory as zip file)
    success = unzipper.recursive_unzip(zip_file)
    
    if success:
        stats = unzipper.get_stats()
        print(f"Extraction completed successfully!")
        print(f"Total extractions: {stats['total_extractions']}")
        print(f"Files processed: {stats['processed_files']}")
    else:
        print("Extraction failed!")


def example_custom_output():
    """Example with custom output directory."""
    
    unzipper = RecursiveUnzipper(log_level='DEBUG')
    
    zip_file = Path("complex_archive.zip")
    output_dir = Path("./extracted_files")
    
    # Extract to custom directory
    success = unzipper.recursive_unzip(zip_file, output_dir)
    
    return success


def example_batch_processing():
    """Example of processing multiple zip files."""
    
    unzipper = RecursiveUnzipper(log_level='INFO')
    
    # List of zip files to process
    zip_files = [
        "archive1.zip",
        "archive2.zip",
        "archive3.zip"
    ]
    
    results = {}
    
    for zip_file in zip_files:
        zip_path = Path(zip_file)
        if zip_path.exists():
            print(f"\nProcessing {zip_file}...")
            success = unzipper.recursive_unzip(zip_path)
            results[zip_file] = success
        else:
            print(f"Skipping {zip_file} - file not found")
            results[zip_file] = False
    
    # Print summary
    print("\n=== Batch Processing Summary ===")
    for zip_file, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{zip_file}: {status}")
    
    # Overall stats
    stats = unzipper.get_stats()
    print(f"\nTotal extractions across all files: {stats['total_extractions']}")


if __name__ == "__main__":
    print("Recursive Unzipper - Example Usage")
    print("=" * 40)
    
    # Run basic example if test files exist
    if Path("test_nested_archive.zip").exists():
        print("\n1. Running basic usage example...")
        example_basic_usage()
    else:
        print("\n1. No test files found. Run create_test_archives.py first.")
    
    print("\n2. Example code for custom output directory:")
    print("   See example_custom_output() function")
    
    print("\n3. Example code for batch processing:")
    print("   See example_batch_processing() function")
