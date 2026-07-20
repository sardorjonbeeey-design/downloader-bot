"""
TikTok downloader service - Cookie Support
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    """TikTok content downloader with cookie support"""
    
    def __init__(self):
        super().__init__()
        self.cookies_file = Path('cookies.txt')
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            opts = self.get_ydl_opts('best')
            opts.update({
                'extract_flat': False,
                'sleep_interval': 3,
            })
            
            if self.cookies_file.exists():
                opts['cookiefile'] = str(self.cookies_file)
                logger.info("✅ Using cookies.txt for TikTok")
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                return None
            
            is_slideshow = 'photo' in str(url).lower() or 'slides' in str(url).lower()
            content_type = 'video' if not is_slideshow else 'photo'
            
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': '✓ TikTok content downloaded',
                'source': 'tiktok',
                'no_watermark': True
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}", exc_info=True)
            return None

tiktok_service = TikTokService()

async def download_tiktok(url: str) -> Optional[Dict[str, Any]]:
    return await tiktok_service.download_content(url)