"""
TikTok downloader - Uses single Cobalt client
"""
import logging
from typing import Dict, Any, Optional

from services.cobalt import cobalt
from services.downloader import DownloaderService

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        file_path = await cobalt.download(url)
        if not file_path:
            return None
        
        is_photo = file_path.suffix in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return {
            'file_path': str(file_path),
            'type': 'photo' if is_photo else 'video',
            'caption': f'✅ TikTok downloaded',
            'source': 'tiktok'
        }

tiktok_service = TikTokService()

async def download_tiktok(url: str):
    return await tiktok_service.download_content(url)