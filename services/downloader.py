"""
Base downloader service using yt-dlp - Fixed
"""
import asyncio
import yt_dlp
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from config import config
from utils.helpers import ensure_directory

logger = logging.getLogger(__name__)

class DownloaderService:
    """Core downloader service with yt-dlp integration"""
    
    def __init__(self):
        self.download_path = Path(config.DOWNLOAD_PATH)
        ensure_directory(self.download_path)
        
    def get_base_opts(self) -> Dict[str, Any]:
        """Get base yt-dlp options"""
        return {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'retries': 10,
            'fragment_retries': 10,
            'skip_download': False,
        }
    
    async def download(self, url: str, options: Dict[str, Any]) -> Optional[Path]:
        """Download content using yt-dlp"""
        def sync_download():
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return None
                    
                    filename = ydl.prepare_filename(info)
                    return Path(filename) if Path(filename).exists() else None
            except yt_dlp.utils.DownloadError as e:
                if "private" in str(e).lower():
                    logger.warning(f"Private content: {url}")
                else:
                    logger.error(f"Download error: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Download error: {str(e)}")
                return None
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sync_download)
        return result
    
    def get_ydl_opts(self, format_spec: str, output_template: str = '%(title)s.%(ext)s') -> Dict[str, Any]:
        """Get yt-dlp options for specific format"""
        opts = self.get_base_opts()
        opts.update({
            'format': format_spec,
            'outtmpl': str(self.download_path / output_template),
            'merge_output_format': 'mp4',
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                }
            ]
        })
        return opts

downloader_service = DownloaderService()

async def download_content(url: str, format_spec: str = 'best') -> Optional[Path]:
    """Convenience function to download content"""
    opts = downloader_service.get_ydl_opts(format_spec)
    return await downloader_service.download(url, opts)