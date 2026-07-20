"""
TikTok downloader - Using Cobalt
"""
import logging
from typing import Dict, Any, Optional

from services.cobalt import cobalt
from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    """TikTok content downloader using Cobalt"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download TikTok content - returns file_data directly"""
        try:
            file_data, filename, error = await cobalt.download(url)
            
            if error:
                logger.error(f"TikTok error: {error}")
                return None
            
            if not file_data:
                return None
            
            # Determine content type from filename
            is_photo = filename and any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
            
            return {
                'file_data': file_data,
                'filename': filename or 'tiktok_video.mp4',
                'type': 'photo' if is_photo else 'video',
                'caption': '✅ TikTok downloaded',
                'no_watermark': True
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}", exc_info=True)
            return None

tiktok_service = TikTokService()

async def download_tiktok(url: str):
    """Download TikTok content"""
    return await tiktok_service.download_content(url)