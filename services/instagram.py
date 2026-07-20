"""
Instagram downloader service - Using your Cobalt instance
"""
import logging
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional

from services.downloader import DownloaderService
from config import config

logger = logging.getLogger(__name__)

class InstagramService(DownloaderService):
    """Instagram content downloader using your Cobalt instance"""
    
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
                    
                    filename = data.get('filename', 'instagram_media.mp4')
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
        """Download Instagram content using Cobalt"""
        try:
            file_path = await self.download_with_cobalt(url)
            
            if not file_path or not file_path.exists():
                return None
            
            content_type = 'photo'
            if file_path.suffix in ['.mp4', '.mov', '.webm']:
                content_type = 'video'
                
            return {
                'file_path': str(file_path),
                'type': content_type,
                'caption': '✅ Instagram content downloaded',
                'source': 'instagram'
            }
            
        except Exception as e:
            logger.error(f"Instagram download error: {str(e)}", exc_info=True)
            return None

instagram_service = InstagramService()

async def download_instagram(url: str) -> Optional[Dict[str, Any]]:
    """Download Instagram content"""
    return await instagram_service.download_content(url)