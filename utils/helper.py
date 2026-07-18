"""
Utility helper functions
"""
import os
import re
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from config import config

logger = logging.getLogger(__name__)

def ensure_directory(path: Path) -> None: