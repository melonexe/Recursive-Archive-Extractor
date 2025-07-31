#!/usr/bin/env python3
"""
Recursive Archive Extractor - PyQt6 GUI

A single-file PyQt6 application for recursively extracting nested archive files.
Supports ZIP, TAR, and GZIP formats.

Author: GitHub Copilot
Date: July 31, 2025
"""

import sys
import os
import zipfile
import tarfile
import gzip
import shutil
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QProgressBar, QStatusBar, QFileDialog, QMessageBox,
    QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class ArchiveExtractor:
    """Core archive extraction functionality."""
    
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
        self.setup_logging(log_level)
        self.processed_files: Set[str] = set()
        self.extraction_count = 0
        self.cleanup_zips = cleanup_zips
        self.total_archive_size = 0
        self.total_extracted_size = 0
        
    def setup_logging(self, log_level: str) -> None:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.2f} {size_names[i]}"
    
    def get_directory_size(self, directory: Path) -> int:
        """Calculate total size of all files in a directory recursively."""
        total_size = 0
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        pass  # Skip files we can't access
        except (OSError, PermissionError):
            pass
        return total_size
        
    def get_archive_type(self, file_path: Path) -> str:
        file_str = str(file_path).lower()
        for ext, archive_type in self.ARCHIVE_EXTENSIONS.items():
            if file_str.endswith(ext):
                return archive_type
        return None
            
    def is_archive_file(self, file_path: Path) -> bool:
        archive_type = self.get_archive_type(file_path)
        if not archive_type:
            return False
            
        try:
            if archive_type == 'zip':
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.testzip()
                    return True
            elif archive_type == 'tar':
                with tarfile.open(file_path, 'r') as tf:
                    tf.getnames()
                    return True
            elif archive_type == 'gzip':
                with gzip.open(file_path, 'rb') as gz:
                    gz.read(1)
                    return True
        except Exception:
            return False
        return False
            
    def extract_archive_file(self, archive_path: Path, extract_to: Path) -> bool:
        try:
            # Track archive size before extraction
            archive_size = archive_path.stat().st_size
            self.total_archive_size += archive_size
            
            self.logger.info(f"Extracting: {archive_path} ({self.format_size(archive_size)}) to {extract_to}")
            extract_to.mkdir(parents=True, exist_ok=True)
            
            # Get size before extraction for this specific directory
            size_before = self.get_directory_size(extract_to)
            
            archive_type = self.get_archive_type(archive_path)
            
            if archive_type == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(extract_to)
            elif archive_type == 'tar':
                with tarfile.open(archive_path, 'r') as tf:
                    tf.extractall(extract_to)
            elif archive_type == 'gzip':
                output_file = extract_to / archive_path.stem
                with gzip.open(archive_path, 'rb') as gz_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(gz_in, f_out)
                self.logger.info(f"Extracted gzip file to: {output_file}")
            else:
                self.logger.error(f"Unsupported archive type for {archive_path}")
                return False
            
            # Calculate size after extraction for this specific directory
            size_after = self.get_directory_size(extract_to)
            extracted_size = size_after - size_before
            self.total_extracted_size += extracted_size
            
            self.extraction_count += 1
            self.logger.info(f"Successfully extracted {archive_path} - Extracted: {self.format_size(extracted_size)}")
            
            # Cleanup if requested
            if self.cleanup_zips:
                try:
                    archive_path.unlink()
                    self.logger.info(f"Removed archive file: {archive_path}")
                except Exception as e:
                    self.logger.warning(f"Could not remove {archive_path}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to extract {archive_path}: {e}")
            return False
            
    def find_archive_files(self, directory: Path) -> List[Path]:
        archive_files = []
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    if self.get_archive_type(item):
                        abs_path = str(item.absolute())
                        if abs_path not in self.processed_files:
                            if self.is_archive_file(item):
                                archive_files.append(item)
                                self.processed_files.add(abs_path)
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing directory {directory}: {e}")
        return archive_files
        
    def recursive_unzip(self, archive_path: Path, base_extract_dir: Path = None) -> bool:
        if not archive_path.exists():
            self.logger.error(f"Archive file not found: {archive_path}")
            return False
            
        if not self.is_archive_file(archive_path):
            self.logger.error(f"Invalid archive file: {archive_path}")
            return False
            
        if base_extract_dir is None:
            base_extract_dir = archive_path.parent / archive_path.stem
            
        self.logger.info(f"Starting recursive extraction of {archive_path}")
        self.logger.info(f"Base extraction directory: {base_extract_dir}")
        
        self.processed_files.add(str(archive_path.absolute()))
        
        if not self.extract_archive_file(archive_path, base_extract_dir):
            return False
            
        iteration = 1
        while True:
            self.logger.info(f"Iteration {iteration}: Searching for nested archive files...")
            nested_archives = self.find_archive_files(base_extract_dir)
            
            if not nested_archives:
                self.logger.info("No more nested archive files found. Extraction complete!")
                break
                
            self.logger.info(f"Found {len(nested_archives)} nested archive file(s) to extract")
            
            for archive in nested_archives:
                if not self.extract_archive_file(archive, archive.parent / archive.stem):
                    self.logger.warning(f"Failed to extract {archive}, continuing with others...")
                    
            iteration += 1
            if iteration > 100:  # Safety limit
                self.logger.warning("Reached maximum iteration limit (100). Stopping extraction.")
                break
                
        self.logger.info(f"Recursive extraction completed!")
        self.logger.info(f"📊 EXTRACTION SUMMARY:")
        self.logger.info(f"   • Total extractions: {self.extraction_count}")
        self.logger.info(f"   • Total archive size: {self.format_size(self.total_archive_size)}")
        self.logger.info(f"   • Total extracted size: {self.format_size(self.total_extracted_size)}")
        
        if self.total_archive_size > 0:
            compression_ratio = ((self.total_archive_size - self.total_extracted_size) / self.total_archive_size) * 100
            if compression_ratio > 0:
                self.logger.info(f"   • Compression ratio: {compression_ratio:.1f}% (saved {self.format_size(self.total_archive_size - self.total_extracted_size)})")
            else:
                expansion_ratio = abs(compression_ratio)
                self.logger.info(f"   • Expansion ratio: {expansion_ratio:.1f}% (expanded by {self.format_size(self.total_extracted_size - self.total_archive_size)})")
        
        return True
        
    def get_stats(self) -> dict:
        stats = {
            'total_extractions': self.extraction_count,
            'processed_files': len(self.processed_files),
            'total_archive_size': self.total_archive_size,
            'total_extracted_size': self.total_extracted_size,
            'total_archive_size_formatted': self.format_size(self.total_archive_size),
            'total_extracted_size_formatted': self.format_size(self.total_extracted_size)
        }
        
        # Calculate compression/expansion ratio
        if self.total_archive_size > 0:
            ratio = ((self.total_archive_size - self.total_extracted_size) / self.total_archive_size) * 100
            stats['compression_ratio'] = ratio
            if ratio > 0:
                stats['size_difference'] = f"Compression: {ratio:.1f}% (saved {self.format_size(self.total_archive_size - self.total_extracted_size)})"
            else:
                stats['size_difference'] = f"Expansion: {abs(ratio):.1f}% (expanded by {self.format_size(self.total_extracted_size - self.total_archive_size)})"
        else:
            stats['compression_ratio'] = 0
            stats['size_difference'] = "No size comparison available"
        
        return stats


class LogHandler(logging.Handler):
    """Custom logging handler to send logs to the GUI."""
    
    def __init__(self, log_signal):
        super().__init__()
        self.log_signal = log_signal
    
    def emit(self, record):
        log_entry = self.format(record)
        self.log_signal.emit(log_entry)


class ExtractionWorker(QThread):
    """Worker thread for running archive extraction."""
    
    finished = pyqtSignal(bool, dict)
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    def __init__(self, archive_path: Path, output_dir: Optional[Path], 
                 log_level: str, cleanup_zips: bool, show_stats: bool):
        super().__init__()
        self.archive_path = archive_path
        self.output_dir = output_dir
        self.log_level = log_level
        self.cleanup_zips = cleanup_zips
        self.show_stats = show_stats
        
    def run(self):
        try:
            extractor = ArchiveExtractor(
                log_level=self.log_level,
                cleanup_zips=self.cleanup_zips
            )
            
            log_handler = LogHandler(self.log_message)
            log_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            extractor.logger.addHandler(log_handler)
            
            success = extractor.recursive_unzip(self.archive_path, self.output_dir)
            
            result_data = {'archive_path': self.archive_path}
            if self.show_stats:
                result_data['stats'] = extractor.get_stats()
            
            self.finished.emit(success, result_data)
            
        except Exception as e:
            self.error.emit(str(e))


class RecursiveArchiveExtractorGUI(QMainWindow):
    """Main GUI application."""
    
    def __init__(self):
        super().__init__()
        self.extraction_worker = None
        self.is_extracting = False
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("Recursive Archive Extractor")
        self.setMinimumSize(800, 700)
        self.resize(900, 800)
        self.center_window()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section
        top_widget = self.create_controls()
        main_splitter.addWidget(top_widget)
        
        # Bottom section
        bottom_widget = self.create_log_section()
        main_splitter.addWidget(bottom_widget)
        
        main_splitter.setSizes([400, 400])
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to extract archive files")
        
    def create_controls(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Recursive Archive Extractor")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QGridLayout(file_group)
        
        file_layout.addWidget(QLabel("Archive File:"), 0, 0)
        self.archive_path_edit = QLineEdit()
        self.archive_path_edit.setPlaceholderText("Select an archive file to extract...")
        file_layout.addWidget(self.archive_path_edit, 0, 1)
        self.browse_archive_btn = QPushButton("Browse...")
        file_layout.addWidget(self.browse_archive_btn, 0, 2)
        
        file_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Optional: leave empty to extract next to archive")
        file_layout.addWidget(self.output_dir_edit, 1, 1)
        self.browse_output_btn = QPushButton("Browse...")
        file_layout.addWidget(self.browse_output_btn, 1, 2)
        
        file_layout.setColumnStretch(1, 1)
        layout.addWidget(file_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Log Level:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        options_layout.addWidget(self.log_level_combo, 0, 1, Qt.AlignmentFlag.AlignLeft)
        
        self.cleanup_checkbox = QCheckBox("Remove archive files after extraction")
        options_layout.addWidget(self.cleanup_checkbox, 1, 0, 1, 3)
        
        self.stats_checkbox = QCheckBox("Show extraction statistics")
        self.stats_checkbox.setChecked(True)
        options_layout.addWidget(self.stats_checkbox, 2, 0, 1, 3)
        
        layout.addWidget(options_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.extract_btn = QPushButton("Start Extraction")
        self.extract_btn.setMinimumHeight(40)
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setEnabled(False)
        
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.setMinimumHeight(40)
        
        buttons_layout.addWidget(self.extract_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.clear_logs_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        
        return widget
    
    def create_log_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 0, 15, 15)
        
        log_group = QGroupBox("Extraction Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color: #0078d4;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        return widget
    
    def setup_connections(self):
        self.browse_archive_btn.clicked.connect(self.browse_archive_file)
        self.browse_output_btn.clicked.connect(self.browse_output_directory)
        self.extract_btn.clicked.connect(self.start_extraction)
        self.cancel_btn.clicked.connect(self.cancel_extraction)
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.archive_path_edit.textChanged.connect(self.on_archive_path_changed)
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def browse_archive_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Archive File",
            "",
            "Archive files (*.zip *.tar *.tar.gz *.tgz *.tar.bz2 *.tbz2 *.tar.xz *.txz *.gz);;"
            "All files (*.*)"
        )
        if file_path:
            self.archive_path_edit.setText(file_path)
    
    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
    
    def on_archive_path_changed(self, text):
        if text and not self.output_dir_edit.text():
            archive_path = Path(text)
            if archive_path.exists():
                default_output = archive_path.parent / archive_path.stem
                self.output_dir_edit.setText(str(default_output))
    
    def validate_inputs(self) -> bool:
        archive_path = self.archive_path_edit.text()
        if not archive_path:
            QMessageBox.critical(self, "Error", "Please select an archive file.")
            return False
        
        archive_file = Path(archive_path)
        if not archive_file.exists():
            QMessageBox.critical(self, "Error", f"Archive file not found: {archive_file}")
            return False
        
        return True
    
    def start_extraction(self):
        if not self.validate_inputs():
            return
        
        if self.is_extracting:
            QMessageBox.warning(self, "Warning", "Extraction is already in progress.")
            return
        
        archive_path = Path(self.archive_path_edit.text())
        output_dir = Path(self.output_dir_edit.text()) if self.output_dir_edit.text() else None
        log_level = self.log_level_combo.currentText()
        cleanup_zips = self.cleanup_checkbox.isChecked()
        show_stats = self.stats_checkbox.isChecked()
        
        self.is_extracting = True
        self.extract_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_label.setText("Extracting...")
        self.status_bar.showMessage("Extraction in progress...")
        self.log_text.clear()
        
        self.extraction_worker = ExtractionWorker(
            archive_path, output_dir, log_level, cleanup_zips, show_stats
        )
        self.extraction_worker.finished.connect(self.on_extraction_finished)
        self.extraction_worker.error.connect(self.on_extraction_error)
        self.extraction_worker.log_message.connect(self.on_log_message)
        self.extraction_worker.start()
    
    def cancel_extraction(self):
        if self.extraction_worker:
            reply = QMessageBox.question(
                self, "Cancel", "Cancel extraction?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.extraction_worker.terminate()
                self.finish_extraction()
                self.log_message("⚠️ Extraction cancelled")
    
    def finish_extraction(self):
        self.is_extracting = False
        self.extract_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Ready")
    
    def on_extraction_finished(self, success: bool, result_data: dict):
        self.finish_extraction()
        
        if success:
            self.status_bar.showMessage("Extraction completed successfully")
            if 'stats' in result_data:
                stats = result_data['stats']
                QMessageBox.information(
                    self, "Extraction Complete", 
                    f"✅ Extraction completed successfully!\n\n"
                    f"📊 Statistics:\n"
                    f"• Total extractions: {stats['total_extractions']}\n"
                    f"• Files processed: {stats['processed_files']}\n"
                    f"• Archive size: {stats['total_archive_size_formatted']}\n"
                    f"• Extracted size: {stats['total_extracted_size_formatted']}\n"
                    f"• {stats['size_difference']}"
                )
            else:
                QMessageBox.information(self, "Complete", "✅ Extraction completed!")
        else:
            self.status_bar.showMessage("Extraction failed")
            QMessageBox.critical(self, "Failed", "❌ Extraction failed")
    
    def on_extraction_error(self, error_message: str):
        self.finish_extraction()
        self.status_bar.showMessage("Extraction failed")
        QMessageBox.critical(self, "Error", f"❌ Error: {error_message}")
    
    def on_log_message(self, message: str):
        self.log_text.append(message)
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"{timestamp} - INFO - {message}")
    
    def clear_logs(self):
        self.log_text.clear()
        self.status_bar.showMessage("Logs cleared")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Recursive Archive Extractor")
    
    # Apply dark mode styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
            background-color: #353535;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        QLineEdit {
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 8px;
            font-size: 11pt;
            background-color: #404040;
            color: #ffffff;
            selection-background-color: #0066cc;
        }
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        QPushButton {
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 16px;
            background-color: #404040;
            color: #ffffff;
            font-size: 11pt;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            border: 1px solid #666666;
        }
        QPushButton:pressed {
            background-color: #353535;
        }
        QPushButton:disabled {
            color: #777777;
            background-color: #2b2b2b;
            border: 1px solid #444444;
        }
        QComboBox {
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 6px;
            font-size: 11pt;
            background-color: #404040;
            color: #ffffff;
        }
        QComboBox:hover {
            border: 2px solid #666666;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #404040;
        }
        QComboBox::down-arrow {
            border: none;
            background-color: transparent;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #0078d4;
        }
        QCheckBox {
            font-size: 11pt;
            color: #ffffff;
            background-color: transparent;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            background-color: #404040;
            border: 2px solid #555555;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
        }
        QCheckBox::indicator:hover {
            border: 2px solid #666666;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 4px;
            background-color: #404040;
            color: #ffffff;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        QStatusBar {
            background-color: #353535;
            color: #ffffff;
            border-top: 1px solid #555555;
        }
        QSplitter::handle {
            background-color: #555555;
        }
        QSplitter::handle:hover {
            background-color: #666666;
        }
    """)
    
    window = RecursiveArchiveExtractorGUI()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
