"""
TikTok downloader service - Using your Cobalt instance
"""
import logging
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional

from services.downloader import DownloaderService
from config import config

logger = logging.getLogger(__name__)

class TikTokService(DownloaderService):
    """TikTok content downloader using your Cobalt instance"""
    
    def __init__(self):
        super().__init__()
        self.cobalt_api = f"{config.COBALT_API_URL}/api/json"
        logger.info(f"✅ Using Cobalt: {self.cobalt_api}")
    
    async def download_with_cobalt(self, url: str) -> Optional[Path]:
        """Download using your Cobalt instance"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "url": url,
                    "videoQuality": "720",
                    "audioFormat": "mp3",
                    "downloadMode": "auto"
                }
                
                async with session.post(self.cobalt_api, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Cobalt API error: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if data.get('status') != 'ok':
                        logger.error(f"Cobalt error: {data.get('text')}")
                        return None
                    
                    download_url = data.get('url')
                    if not download_url:
                        return None
                    
                    filename = data.get('filename', 'tiktok_video.mp4')
                    filepath = self.download_path / filename
                    
                    async with session.get(download_url) as file_response:
                        if file_response.status == 200:
                            with open(filepath, 'wb') as f:
                                f.write(await file_response.read())
                            return filepath
                        return None
                            
        except Exception as e:
            logger.error(f"Cobalt download error: {str(e)}")
            return None
    
    async def download_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Download TikTok content using Cobalt"""
        try:
            file_path = await self.download_with_cobalt(url)
            
            if not file_path or not file_path.exists():
                return None
            
            is_photo = 'photo' in str(url).lower() or file_path.suffix in ['.jpg', '.jpeg', '.png']
            content_type = 'photo' if is_photo else 'video'
            
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': f'✅ TikTok {content_type} downloaded',
                'source': 'tiktok'
            }
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}", exc_info=True)
            return None

tiktok_service = TikTokService()

async def download_tiktok(url: str) -> Optional[Dict[str, Any]]:
    """Download TikTok content"""
    return await tiktok_service.download_content(url)