"""
Instagram downloader - Using Cobalt
"""
import logging
from typing import Dict, Any, Optional

from services.cobalt import cobalt
from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class InstagramService(DownloaderService):
    """Instagram content downloader using Cobalt"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download Instagram content - returns file_data directly"""
        try:
            file_data, filename, error = await cobalt.download(url)
            
            if error:
                logger.error(f"Instagram error: {error}")
                return None
            
            if not file_data:
                return None
            
            # Determine content type from filename
            is_video = filename and any(ext in filename.lower() for ext in ['.mp4', '.mov', '.webm'])
            
            return {
                'file_data': file_data,
                'filename': filename or 'instagram_media.mp4',
                'type': 'video' if is_video else 'photo',
                'caption': '✅ Instagram downloaded'
            }
            
        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}", exc_info=True)
            return None

instagram_service = InstagramService()

async def download_instagram(url: str):
    """Download Instagram content"""
    return await instagram_service.download_content(url)