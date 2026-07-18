"""
TikTok downloader service
"""
import json
import logging
from typing import Dict, Any, Optional

from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    """TikTok content downloader"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download TikTok content (video or photo slides)
        
        Args:
            url: TikTok URL
            
        Returns:
            Dictionary with file info and metadata
        """
        try:
            # TikTok requires special options for watermark removal
            opts = self.get_ydl_opts('best')
            opts.update({
                'cookiesfrombrowser': ('chrome',),
                'extract_flat': False,
                'sleep_interval': 3,  # Rate limiting
            })
            
            file_path = await self.download(url, opts)
            
            if not file_path or not file_path.exists():
                return None
            
            # Check if it's a photo slideshow
            is_slideshow = False
            if 'photo' in str(url).lower() or 'slides' in str(url).lower():
                is_slideshow = True
            
            content_type = 'video' if not is_slideshow else 'photo'
            
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': '🎵 TikTok content downloaded successfully!',
                'source': 'tiktok',
                'no_watermark': True
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}", exc_info=True)
            return None

# Singleton instance
tiktok_service = TikTokService()

async def download_tiktok(url: str) -> Optional[Dict[str, Any]]:
    """Download TikTok content"""
    return await tiktok_service.download_content(url)