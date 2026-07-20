"""
Pinterest downloader - Using Cobalt
"""
import logging
from typing import Dict, Any, Optional, Tuple

from services.cobalt import cobalt
from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class PinterestService(DownloaderService):
    """Pinterest content downloader using Cobalt"""
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download Pinterest content - images or videos"""
        try:
            file_data, filename, error = await cobalt.download(url)
            
            if error:
                logger.error(f"Pinterest error: {error}")
                return None
            
            if not file_data:
                return None
            
            # Determine content type from filename
            is_video = filename and any(ext in filename.lower() for ext in ['.mp4', '.mov', '.webm'])
            
            return {
                'file_data': file_data,
                'filename': filename or 'pinterest_media.mp4',
                'type': 'video' if is_video else 'photo',
                'caption': '✅ Pinterest downloaded'
            }
            
        except Exception as e:
            logger.error(f"Pinterest download error: {str(e)}", exc_info=True)
            return None

pinterest_service = PinterestService()

async def download_pinterest(url: str):
    """Download Pinterest content"""
    return await pinterest_service.download_content(url)