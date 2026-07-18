"""
Utility helper functions
"""
import re
import os
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import logging

from config import config

logger = logging.getLogger(__name__)

def ensure_directory(path: Union[str, Path]) -> None:
    """Ensure directory exists - handles file conflicts"""
    # Convert to Path if string
    if isinstance(path, str):
        path = Path(path)
    
    try:
        # If it exists and is a file, delete it and create directory
        if path.exists() and not path.is_dir():
            logger.warning(f"Removing file '{path}' to create directory")
            path.unlink()
            path.mkdir(parents=True)
            logger.info(f"Created directory: {path}")
        elif not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created directory: {path}")
        else:
            logger.debug(f"Directory already exists: {path}")
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        raise

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def cleanup_file(file_path: str) -> None:
    """Clean up downloaded file"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.debug(f"Cleaned up: {file_path}")
            
        # Also remove thumbnail files
        for thumb in path.parent.glob(f"{path.stem}.*.jpg"):
            thumb.unlink()
            
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def get_timestamp() -> str:
    """Get current timestamp for unique filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def is_within_size_limit(file_size: int) -> bool:
    """Check if file is within size limit"""
    max_size = config.MAX_FILE_SIZE * 1024 * 1024
    return file_size <= max_size