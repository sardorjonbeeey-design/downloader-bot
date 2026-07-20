"""
TikTok downloader service - Supports videos and photos
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    """TikTok content downloader - videos + photos"""
    
    def __init__(self):
        super().__init__()
        self.cookies_file = Path('cookies.txt')
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download TikTok content (video or photo)"""
        try:
            opts = self.get_ydl_opts('best')
            opts.update({
                'extract_flat': False,
                'sleep_interval': 3,
                'ignoreerrors': True,
            })
            
            if self.cookies_file.exists():
                opts['cookiefile'] = str(self.cookies_file)
                logger.info("✅ Using cookies.txt for TikTok")
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                # Try alternative format for photos
                logger.info("Trying alternative download for TikTok photo...")
                opts2 = self.get_ydl_opts('bestvideo+bestaudio/best')
                opts2.update({
                    'extract_flat': False,
                    'sleep_interval': 3,
                    'ignoreerrors': True,
                })
                if self.cookies_file.exists():
                    opts2['cookiefile'] = str(self.cookies_file)
                file_path = await self.download(url, opts2)
                
                if not file_path or not file_path.exists():
                    return None
            
            # Determine content type
            is_photo = 'photo' in str(url).lower() or file_path.suffix in ['.jpg', '.jpeg', '.png']
            content_type = 'photo' if is_photo else 'video'
            
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': f'✓ TikTok {content_type} downloaded',
                'source': 'tiktok',
                'no_watermark': True
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}", exc_info=True)
            return None

tiktok_service = TikTokService()

async def download_tiktok(url: str) -> Optional[Dict[str, Any]]:
    """Download TikTok content"""
    return await tiktok_service.download_content(url)