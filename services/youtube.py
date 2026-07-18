"""
YouTube downloader service
"""
import json
import logging
import yt_dlp
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

from services.downloader import DownloaderService
from config import config
from utils.helpers import format_file_size

logger = logging.getLogger(__name__)

class YouTubeService(DownloaderService):
    """YouTube content downloader"""
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information and available qualities
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video info and quality options
        """
        try:
            opts = self.get_base_opts()
            opts.update({
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
            })
            
            def sync_extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, sync_extract)
            
            if not info:
                return None
            
            # Extract available formats
            qualities = {}
            for quality_key, quality_info in config.YOUTUBE_QUALITIES.items():
                try:
                    # Get file size for this quality
                    format_spec = quality_info['format']
                    size_info = await self._get_format_size(url, format_spec)
                    qualities[quality_key] = {
                        'label': quality_info['label'],
                        'format': format_spec,
                        'size': size_info
                    }
                except Exception as e:
                    logger.warning(f"Could not get size for {quality_key}: {e}")
                    qualities[quality_key] = {
                        'label': quality_info['label'],
                        'format': format_spec,
                        'size': None
                    }
            
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'duration': self._format_duration(info.get('duration', 0)),
                'duration_seconds': info.get('duration', 0),
                'url': url,
                'qualities': qualities,
                'thumbnail': info.get('thumbnail')
            }
            
        except Exception as e:
            logger.error(f"YouTube info error: {str(e)}", exc_info=True)
            return None
    
    async def _get_format_size(self, url: str, format_spec: str) -> Optional[str]:
        """Get file size for specific format"""
        try:
            opts = self.get_base_opts()
            opts.update({
                'extract_flat': True,
                'quiet': True,
            })
            
            def sync_get_size():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        # Try to get file size
                        for f in info.get('formats', []):
                            if f.get('format_id') == format_spec:
                                size = f.get('filesize') or f.get('filesize_approx')
                                if size:
                                    return format_file_size(size)
                return None
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, sync_get_size)
            
        except Exception:
            return None
    
    async def download_video(self, url: str, quality: str = '720p') -> Optional[Dict[str, Any]]:
        """
        Download YouTube video with specified quality
        
        Args:
            url: YouTube URL
            quality: Quality key (360p, 480p, 720p, 1080p)
            
        Returns:
            Dictionary with file info
        """
        try:
            if quality not in config.YOUTUBE_QUALITIES:
                quality = '720p'
            
            quality_info = config.YOUTUBE_QUALITIES[quality]
            format_spec = quality_info['format']
            
            opts = self.get_ydl_opts(format_spec)
            opts.update({
                'merge_output_format': 'mp4',
            })
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                return None
            
            return {
                'file_path': str(file_path),
                'type': 'video',
                'caption': f'▶️ YouTube video downloaded successfully!',
                'source': 'youtube'
            }
            
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}", exc_info=True)
            return None
    
    async def download_audio(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download audio from YouTube as MP3
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with file info
        """
        try:
            opts = self.get_base_opts()
            opts.update({
                'format': 'bestaudio/best',
                'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }
                ],
                'writethumbnail': True,
                'quiet': True,
            })
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                return None
            
            # Get MP3 file
            mp3_path = file_path.with_suffix('.mp3')
            if mp3_path.exists():
                return {
                    'file_path': str(mp3_path),
                    'type': 'audio',
                    'caption': '🎵 Audio downloaded successfully!',
                    'source': 'youtube'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"YouTube audio download error: {str(e)}", exc_info=True)
            return None
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in human readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

# Singleton instance
youtube_service = YouTubeService()

async def download_youtube(url: str, quality: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Download YouTube content
    
    Args:
        url: YouTube URL
        quality: Quality to download (if None, returns info for selection)
        
    Returns:
        Dictionary with file info or video info for quality selection
    """
    if not quality:
        # Return video info for quality selection
        return await youtube_service.get_video_info(url)
    else:
        # Download with specific quality
        return await youtube_service.download_video(url, quality)

async def download_youtube_audio(url: str) -> Optional[Dict[str, Any]]:
    """Download YouTube audio as MP3"""
    return await youtube_service.download_audio(url)