"""
Instagram downloader - Uses single Cobalt client
"""
import logging
from typing import Dict, Any, Optional

from services.cobalt import cobalt
from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class InstagramService(DownloaderService):
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        file_path = await cobalt.download(url)
        if not file_path:
            return None
        
        is_video = file_path.suffix in ['.mp4', '.mov', '.webm']
        return {
            'file_path': str(file_path),
            'type': 'video' if is_video else 'photo',
            'caption': '✅ Instagram downloaded',
            'source': 'instagram'
        }

instagram_service = InstagramService()

async def download_instagram(url: str):
    return await instagram_service.download_content(url)