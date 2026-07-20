"""
Cobalt API - Single Source of Truth
All TikTok and Instagram downloads go through this ONE file
"""
import aiohttp
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from config import config

logger = logging.getLogger(__name__)

class CobaltClient:
    """Single Cobalt client - Update ONCE, works everywhere"""
    
    def __init__(self):
        self.api_url = config.COBALT_API_URL
        logger.info(f"✅ Cobalt API: {self.api_url}")
    
    async def download(self, url: str) -> Optional[Path]:
        """Download ANY content (TikTok, Instagram, etc)"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "url": url,
                    "videoQuality": "720",
                    "audioFormat": "mp3",
                    "downloadMode": "auto"
                }
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"❌ Cobalt error: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    if data.get('status') != 'ok':
                        logger.error(f"❌ Cobalt: {data.get('text')}")
                        return None
                    
                    download_url = data.get('url')
                    if not download_url:
                        return None
                    
                    filename = data.get('filename', 'download.mp4')
                    filepath = Path(config.DOWNLOAD_PATH) / filename
                    
                    async with session.get(download_url) as file_response:
                        if file_response.status == 200:
                            with open(filepath, 'wb') as f:
                                f.write(await file_response.read())
                            logger.info(f"✅ Downloaded: {filepath}")
                            return filepath
                        return None
                            
        except Exception as e:
            logger.error(f"❌ Cobalt error: {str(e)}")
            return None

# ONE instance - use this everywhere
cobalt = CobaltClient()