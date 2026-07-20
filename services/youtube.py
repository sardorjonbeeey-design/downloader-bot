"""
YouTube downloader - With streaming support
"""
import logging
import yt_dlp
import asyncio
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from config import config

logger = logging.getLogger(__name__)

class YouTubeService:
    """YouTube downloader with streaming support"""
    
    def __init__(self):
        self.cookies_file = Path('cookies.txt')
    
    def get_auth_opts(self) -> Dict[str, Any]:
        """Get authentication options"""
        opts = {
            'sleep_interval': 5,
            'max_sleep_interval': 30,
            'quiet': True,
            'no_warnings': True,
        }
        
        if self.cookies_file.exists():
            opts['cookiefile'] = str(self.cookies_file)
            logger.info("✅ Using cookies.txt for YouTube")
        
        return opts
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information"""
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                **self.get_auth_opts()
            }
            
            def sync_extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, sync_extract)
            
            if not info:
                return None
            
            # Format duration
            duration = info.get('duration', 0)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
            
            # Get qualities
            qualities = {}
            for quality_key, quality_info in config.YOUTUBE_QUALITIES.items():
                qualities[quality_key] = {
                    'label': quality_info['label'],
                    'format': quality_info['format'],
                    'size': None
                }
            
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'duration': duration_str,
                'duration_seconds': duration,
                'url': url,
                'qualities': qualities,
                'thumbnail': info.get('thumbnail')
            }
            
        except Exception as e:
            logger.error(f"YouTube info error: {str(e)}")
            return None
    
    async def download_video(self, url: str, quality: str = '720p') -> Optional[Dict[str, Any]]:
        """Download video and return file data"""
        try:
            if quality not in config.YOUTUBE_QUALITIES:
                quality = '720p'
            
            quality_info = config.YOUTUBE_QUALITIES[quality]
            format_spec = quality_info['format']
            
            opts = {
                'quiet': True,
                'no_warnings': True,
                'format': format_spec,
                'merge_output_format': 'mp4',
                **self.get_auth_opts()
            }
            
            def sync_download():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return None
                    filename = ydl.prepare_filename(info)
                    if Path(filename).exists():
                        return Path(filename)
                    return None
            
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(None, sync_download)
            
            if not file_path or not file_path.exists():
                return None
            
            # Read file into memory (streaming directly)
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Clean up
            file_path.unlink()
            
            return {
                'file_data': file_data,
                'filename': file_path.name,
                'type': 'video',
                'caption': f'✅ YouTube video downloaded ({quality})'
            }
            
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            return None
    
    async def download_audio(self, url: str) -> Optional[Dict[str, Any]]:
        """Download audio and return file data"""
        try:
            opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }
                ],
                **self.get_auth_opts()
            }
            
            def sync_download():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return None
                    filename = ydl.prepare_filename(info).replace('.mp4', '.mp3').replace('.webm', '.mp3')
                    if Path(filename).exists():
                        return Path(filename)
                    return None
            
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(None, sync_download)
            
            if not file_path or not file_path.exists():
                return None
            
            # Read file into memory
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Clean up
            file_path.unlink()
            
            return {
                'file_data': file_data,
                'filename': file_path.name,
                'type': 'audio',
                'title': file_path.stem.replace('.mp3', '')
            }
            
        except Exception as e:
            logger.error(f"YouTube audio error: {str(e)}")
            return None

youtube_service = YouTubeService()

async def download_youtube(url: str, quality: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not quality:
        return await youtube_service.get_video_info(url)
    else:
        return await youtube_service.download_video(url, quality)

async def download_youtube_audio(url: str) -> Optional[Dict[str, Any]]:
    return await youtube_service.download_audio(url)