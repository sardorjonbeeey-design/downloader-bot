import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DOWNLOAD_PATH = Path(os.getenv('DOWNLOAD_PATH', './downloads'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Cobalt API URL
    COBALT_API_URL = os.getenv('COBALT_API_URL', 'https://api.cobalt.tools')
    
    SUPPORTED_PLATFORMS = {
        'instagram': ['instagram.com', 'instagr.am'],
        'tiktok': ['tiktok.com', 'vm.tiktok.com'],
        'youtube': ['youtube.com', 'youtu.be'],
    }
    
    YOUTUBE_QUALITIES = {
        '360p': {'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]', 'label': '360p'},
        '480p': {'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]', 'label': '480p'},
        '720p': {'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]', 'label': '720p'},
        '1080p': {'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]', 'label': '1080p'},
    }

config = Config()