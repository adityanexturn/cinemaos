"""
File Handler Utilities
----------------------
Provides helper functions for file upload, validation, and processing.
This module ensures uploaded files are safe, within size limits, and properly
formatted before being sent to the Gemini File Search API.
"""

import streamlit as st
from pathlib import Path
from config.settings import MAX_FILE_SIZE_MB, ALLOWED_FILE_TYPES
from config.constants import SUPPORTED_FILE_TYPES
from utils.logger import cinema_logger


def validate_uploaded_file(uploaded_file):
    """
    Validate an uploaded file for type and size constraints.
    This prevents users from uploading unsupported or oversized files that could
    cause errors or performance issues in the Gemini File Search API.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    
    # Check file extension against allowed types
    # This ensures only supported document formats are processed
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in ALLOWED_FILE_TYPES:
        error_msg = f"❌ File type '.{file_extension}' not supported. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
        cinema_logger.warning(f"Invalid file type uploaded: {file_extension}")
        return False, error_msg
    
    # Check file size to prevent memory issues and API limits
    # Size is checked in bytes and converted to MB for user-friendly messages
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        error_msg = f"❌ File '{uploaded_file.name}' is {file_size_mb:.2f}MB. Max size: {MAX_FILE_SIZE_MB}MB"
        cinema_logger.warning(f"File too large: {uploaded_file.name} ({file_size_mb:.2f}MB)")
        return False, error_msg
    
    cinema_logger.info(f"File validated successfully: {uploaded_file.name} ({file_size_mb:.2f}MB)")
    return True, None


def get_file_icon(filename):
    """
    Get an appropriate emoji icon based on file extension.
    This improves the UI by providing visual cues for different file types,
    making it easier for users to identify their uploaded documents at a glance.
    
    Args:
        filename: Name of the file including extension
        
    Returns:
        str: Emoji icon representing the file type
    """
    
    # Extract file extension and map to appropriate emoji
    # Icons provide quick visual recognition of file types
    extension = filename.split('.')[-1].lower()
    
    icon_map = {
        'pdf': '📄',
        'txt': '📝',
        'md': '📝',
        'csv': '📊',
        'json': '🔧',
        'docx': '📘',
    }
    
    # Return specific icon or default document icon
    return icon_map.get(extension, '📎')


def format_file_size(size_bytes):
    """
    Convert file size from bytes to human-readable format.
    This makes file sizes more understandable for users by displaying them
    in appropriate units (KB, MB, GB) instead of raw byte counts.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "2.5 MB")
    """
    
    # Convert bytes to appropriate unit for readability
    # Uses 1024 as base for binary file sizes (not 1000)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"
