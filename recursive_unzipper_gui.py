#!/usr/bin/env python3
"""
Recursive Zip Extractor - GUI Version

A simple graphical user interface for the recursive zip extractor tool.
Uses tkinter for cross-platform compatibility.

Author: GitHub Copilot
Date: July 23, 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Import the main unzipper class
from recursive_unzipper import RecursiveUnzipper


class LogHandler(logging.Handler):
    """Custom logging handler to send logs to the GUI."""
    
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """Send log record to the queue."""
        log_entry = self.format(record)
        self.log_queue.put(log_entry)


class RecursiveUnzipperGUI:
    """GUI application for the recursive zip extractor."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        
        # Queue for thread communication - must be created before setup_logging
        self.log_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_logging()
        
        # Start checking for log messages
        self.check_log_queue()
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Recursive Archive Extractor")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Center the window
        self.root.geometry("+{}+{}".format(
            (self.root.winfo_screenwidth() // 2) - 400,
            (self.root.winfo_screenheight() // 2) - 350
        ))
        
    def setup_variables(self):
        """Initialize tkinter variables."""
        self.zip_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.log_level = tk.StringVar(value="INFO")
        self.cleanup_zips = tk.BooleanVar(value=False)
        self.show_stats = tk.BooleanVar(value=True)
        self.is_extracting = False
        
    def setup_ui(self):
        """Create the user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Recursive Archive Extractor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Zip file selection
        ttk.Label(main_frame, text="Archive File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.zip_file_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_zip_file).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir_path, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_output_dir).grid(row=2, column=2, padx=(5, 0), pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Log level
        ttk.Label(options_frame, text="Log Level:").grid(row=0, column=0, sticky=tk.W, pady=2)
        log_level_combo = ttk.Combobox(options_frame, textvariable=self.log_level,
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"],
                                      state="readonly", width=15)
        log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Checkboxes
        ttk.Checkbutton(options_frame, text="Remove archive files after extraction (cleanup)",
                       variable=self.cleanup_zips).grid(row=1, column=0, columnspan=2, 
                                                        sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Show extraction statistics",
                       variable=self.show_stats).grid(row=2, column=0, columnspan=2,
                                                      sticky=tk.W, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Extract button
        self.extract_button = ttk.Button(buttons_frame, text="Start Extraction",
                                        command=self.start_extraction, style="Accent.TButton")
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(buttons_frame, text="Cancel",
                                       command=self.cancel_extraction, state="disabled")
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear logs button
        ttk.Button(buttons_frame, text="Clear Logs",
                  command=self.clear_logs).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Extraction Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to extract archive files")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_logging(self):
        """Set up logging to capture output from the unzipper."""
        self.log_handler = LogHandler(self.log_queue)
        self.log_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        
    def browse_zip_file(self):
        """Open file dialog to select archive file."""
        filename = filedialog.askopenfilename(
            title="Select Archive File",
            filetypes=[
                ("Archive files", "*.zip;*.tar;*.tar.gz;*.tgz;*.tar.bz2;*.tbz2;*.tar.xz;*.txz;*.gz"),
                ("Zip files", "*.zip"),
                ("Tar files", "*.tar;*.tar.gz;*.tgz;*.tar.bz2;*.tbz2;*.tar.xz;*.txz"),
                ("Gzip files", "*.gz"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.zip_file_path.set(filename)
            # Auto-set output directory if not already set
            if not self.output_dir_path.get():
                zip_path = Path(filename)
                default_output = zip_path.parent / zip_path.stem
                self.output_dir_path.set(str(default_output))
                
    def browse_output_dir(self):
        """Open directory dialog to select output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if directory:
            self.output_dir_path.set(directory)
            
    def validate_inputs(self):
        """Validate user inputs before starting extraction."""
        if not self.zip_file_path.get():
            messagebox.showerror("Error", "Please select an archive file.")
            return False
            
        archive_path = Path(self.zip_file_path.get())
        if not archive_path.exists():
            messagebox.showerror("Error", f"Archive file not found: {archive_path}")
            return False
            
        # Check if it's a supported archive format
        supported_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz', '.gz']
        file_str = str(archive_path).lower()
        is_supported = any(file_str.endswith(ext) for ext in supported_extensions)
        
        if not is_supported:
            if not messagebox.askyesno("Warning", 
                                     f"Selected file doesn't appear to be a supported archive format.\n"
                                     f"Supported formats: {', '.join(supported_extensions)}\n"
                                     f"Continue anyway?"):
                return False
                
        return True
        
    def start_extraction(self):
        """Start the extraction process in a separate thread."""
        if not self.validate_inputs():
            return
            
        if self.is_extracting:
            messagebox.showwarning("Warning", "Extraction is already in progress.")
            return
            
        # Update UI state
        self.is_extracting = True
        self.extract_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.progress_bar.start()
        self.progress_label.config(text="Extracting...")
        self.status_var.set("Extraction in progress...")
        
        # Clear previous logs
        self.log_text.delete(1.0, tk.END)
        
        # Start extraction thread
        self.extraction_thread = threading.Thread(target=self.run_extraction)
        self.extraction_thread.daemon = True
        self.extraction_thread.start()
        
    def run_extraction(self):
        """Run the extraction process (called in separate thread)."""
        try:
            # Get parameters
            archive_path = Path(self.zip_file_path.get())
            output_dir = Path(self.output_dir_path.get()) if self.output_dir_path.get() else None
            
            # Create unzipper with GUI logging
            unzipper = RecursiveUnzipper(
                log_level=self.log_level.get(),
                cleanup_zips=self.cleanup_zips.get()
            )
            
            # Add our log handler
            unzipper.logger.addHandler(self.log_handler)
            
            # Run extraction
            success = unzipper.recursive_unzip(archive_path, output_dir)
            
            # Get statistics
            stats = unzipper.get_stats() if self.show_stats.get() else None
            
            # Send result back to main thread
            self.result_queue.put({
                'success': success,
                'stats': stats,
                'archive_path': archive_path
            })
            
        except Exception as e:
            self.result_queue.put({
                'success': False,
                'error': str(e),
                'archive_path': archive_path
            })
            
    def cancel_extraction(self):
        """Cancel the extraction process."""
        if not self.is_extracting:
            return
            
        # Note: This is a simple cancel - in a more advanced version,
        # you could implement proper thread cancellation
        self.finish_extraction()
        self.log_message("⚠️ Extraction cancelled by user", "WARNING")
        
    def finish_extraction(self):
        """Reset UI state after extraction completes or is cancelled."""
        self.is_extracting = False
        self.extract_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.progress_bar.stop()
        self.progress_label.config(text="Ready")
        
    def check_log_queue(self):
        """Check for new log messages and update the GUI."""
        # Process log messages
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
            
        # Check for extraction results
        try:
            result = self.result_queue.get_nowait()
            self.handle_extraction_result(result)
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_log_queue)
        
    def handle_extraction_result(self, result):
        """Handle the completion of extraction."""
        self.finish_extraction()
        
        if 'error' in result:
            self.status_var.set("Extraction failed")
            messagebox.showerror("Extraction Failed", f"Error: {result['error']}")
            self.log_message(f"❌ Extraction failed: {result['error']}", "ERROR")
        elif result['success']:
            self.status_var.set("Extraction completed successfully")
            
            # Show statistics if requested
            if result.get('stats'):
                stats = result['stats']
                stats_message = (f"✅ Extraction completed successfully!\n\n"
                               f"Statistics:\n"
                               f"• Total extractions: {stats['total_extractions']}\n"
                               f"• Files processed: {stats['processed_files']}")
                messagebox.showinfo("Extraction Complete", stats_message)
                self.log_message(f"✅ Successfully completed recursive extraction", "INFO")
                self.log_message(f"📊 Total extractions: {stats['total_extractions']}", "INFO")
                self.log_message(f"📊 Files processed: {stats['processed_files']}", "INFO")
            else:
                messagebox.showinfo("Extraction Complete", "✅ Extraction completed successfully!")
                self.log_message(f"✅ Successfully completed recursive extraction", "INFO")
        else:
            self.status_var.set("Extraction failed")
            messagebox.showerror("Extraction Failed", "Extraction failed for unknown reason.")
            self.log_message("❌ Extraction failed", "ERROR")
            
    def log_message(self, message, level="INFO"):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {level} - {message}"
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Logs cleared")


def main():
    """Main function to run the GUI application."""
    # Create the main window
    root = tk.Tk()
    
    # Apply a modern theme if available
    try:
        # Try to use a modern theme
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
    except:
        pass  # Use default theme if modern themes aren't available
    
    # Create and run the application
    app = RecursiveUnzipperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_extracting:
            if messagebox.askokcancel("Quit", "Extraction is in progress. Do you want to quit?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == '__main__':
    main()
